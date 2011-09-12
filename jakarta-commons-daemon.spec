# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_gcj_support 1

%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define native      %{?_without_native:0}%{!?_without_native:1}

%define base_name   daemon
%define short_name  commons-%{base_name}

Name:           jakarta-%{short_name}
Version:        1.0.1
Release:        8.9%{?dist}
Epoch:          1
Summary:        Defines API to support an alternative invocation mechanism
License:        ASL 2.0
Group:          Applications/System
URL:            http://jakarta.apache.org/commons/daemon/
Source0:        http://www.apache.org/dist/jakarta/commons/daemon/source/daemon-1.0.1.tar.gz
Patch0:          %{name}-crosslink.patch
Patch1:          %{name}-execve-path-warning.patch
Patch2:          %{name}-ia64-configure.patch
Patch3:          %{name}-s390x-configure.patch
Patch4:          %{name}-ppc64-configure.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{native}
BuildRequires:  java-devel
BuildRequires:  xmlto
%endif
%if ! %{gcj_support}
BuildArch:      noarch
%endif
BuildRequires:  ant, java-javadoc
BuildRequires:  jpackage-utils >= 0:1.6
Provides:       %{short_name} = %{epoch}:%{version}-%{release}
Obsoletes:      %{short_name} < %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:       java-gcj-compat-devel
Requires(post):      java-gcj-compat
Requires(postun):    java-gcj-compat
%endif

%description
The scope of this package is to define an API in line with the current
Java(tm) Platform APIs to support an alternative invocation mechanism
which could be used instead of the above mentioned public static void
main(String[]) method.  This specification cover the behavior and life
cycle of what we define as Java(tm) daemons, or, in other words, non
interactive Java(tm) applications.

%package        jsvc
Summary:        Java daemon launcher
Group:          Applications/System
Provides:       jsvc = %{epoch}:%{version}-%{release}

%if %{gcj_support}
BuildRequires:       java-gcj-compat-devel
Requires(post):      java-gcj-compat
Requires(postun):    java-gcj-compat
%endif

%description    jsvc
%{summary}.

%package        javadoc
Summary:        Javadoc for %{name}
Group:          Documentation
Requires(post):   /bin/rm,/bin/ln
Requires(postun): /bin/rm

%description    javadoc
Javadoc for %{name}.


%prep
%setup -q -n %{base_name}-%{version}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0 -b .s390x
%patch4 -p0 -b .ppc
chmod 644 src/samples/*
%if %{native}
pushd src/native/unix
xmlto man man/jsvc.1.xml
popd
%endif
sed -i -e '2425s/powerpc/powerpc*/' src/native/unix/configure


%build
ant -Dant.lib=%{_javadir} -Dj2se.javadoc=%{_javadocdir}/java dist
%if %{native}
cd src/native/unix
%configure --with-java=%{java_home}
make %{?_smp_mflags}
%endif


%install
rm -rf $RPM_BUILD_ROOT
%if %{native}
install -Dpm 755 src/native/unix/jsvc $RPM_BUILD_ROOT%{_bindir}/jsvc
install -Dpm 0644 src/native/unix/jsvc.1 $RPM_BUILD_ROOT%{_mandir}/man1/jsvc.1
%endif
# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -pm 644 dist/%{short_name}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|jakarta-||g"`; done)
(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}*; do ln -sf ${jar} `echo $jar| sed  "s|-%{version}||g"`; done)
# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%if %{native}
%files jsvc
%defattr(-,root,root,-)
%doc LICENSE*
%{_bindir}/jsvc
%{_mandir}/man1/jsvc.1*
%endif

%files
%defattr(-,root,root,-)
%doc LICENSE* PROPOSAL.html RELEASE-NOTES.txt STATUS.html src/samples
%doc src/docs/*
%{_javadir}/*

%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}

%files javadoc
%defattr(-,root,root,-)
%doc %{_javadocdir}/%{name}-%{version}
%doc %{_javadocdir}/%{name}

%endif

%changelog
* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1:1.0.1-8.9
- Rebuilt for RHEL 6

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.0.1-8.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Mar 03 2009 Karsten Hopp <karsten@redhat.com> 1.0.1-7.8
- ppc needs a similar patch

* Tue Mar 03 2009 Karsten Hopp <karsten@redhat.com> 1.0.1-7.7
- add configure patch for s390x

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.0.1-7.6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:1.0.1-6.6
- drop repotag

* Fri Feb 08 2008 Permaine Cheung <pcheung@redhat.com> - 1:1.0.1-6jpp.5
- Add configure patch for ia64 from Doug Chapman

* Mon Sep 24 2007 Permaine Cheung <pcheung@redhat.com> - 1:1.0.1-6jpp.4
- Add execve path warning patch from James Ralston

* Mon Sep 17 2007 James Ralston <ralston at pobox.com> - 1:1.0.1-6jpp.3
- update License tag to reflect new acceptable licenses
- update main Group tag (old value "System/Boot" is invalid)
- update jsvc Group tag as well
- update javadoc Group tag as well
- building jsvc is no longer mutually exclusive with building javadoc
- jsvc is built by default (use "--without native" to disable)
- build jsvc man page from DocBook source via xmlto; install
- move jsvc from sbindir to bindir (man page is section 1)

* Fri Jan 26 2007 Permaine Cheung <pcheung@redhat.com> - 1:1.0.1-6jpp.2
- Added versioning to provides and obsoletes and rpmlint cleanup

* Thu Aug 17 2006 Deepak Bhole <dbhole@redhat.com> - 1:1.0.1-6jpp.1
- Added missing requirements
- Fixed bug that cause post/postun to not run when built with --with native

* Thu Aug 10 2006 Karsten Hopp <karsten@redhat.de> 1.0.1-4jpp_3fc
- Requires(post):     coreutils

* Wed Jul 19 2006 Deepak Bhole <dbhole@redhat.com> - 1:1.0.1-4jpp_1fc
- Remove name/release/version defines as applicable.

* Mon Jul 17 2006 Deepak Bhole <dbhole@redhat.com> - 1:1.0.1-3jpp
- Added conditional native build.

* Wed Apr 12 2006 Ralph Apel <r.apel at r-apel.de> - 1:1.0.1-2jpp
- First JPP-1.7 release

* Thu Oct 27 2005 Ralph Apel <r.apel at r-apel.de> - 1:1.0.1-1jpp
- Update to 1.0.1

* Sun Aug 23 2004 Randy Watler <rwatler at finali.com> - 1:1.0-2jpp
- Rebuild with ant-1.6.2
* Tue May 18 2004 Ville Skyttä <ville.skytta at iki.fi> - 1:1.0-1jpp
- Update to 1.0.

* Sat Oct 11 2003 Ville Skyttä <ville.skytta at iki.fi> - 1:1.0-0.alpha.1jpp
- Update to 1.0 alpha, bump epoch.
- Non-versioned, crosslinked javadocs.
- Build native jsvc with "--with native".

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0-5jpp
- fix ASF license

* Thu Feb 27 2003 Henri Gomez <hgomez@users.sourceforge.net> 1.0-4jpp
- fix missing packager tag
- get latest nightly (20030227)
- fix ant lib location for javadoc
- added common-launcher jar

* Fri Jul 12 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-3jpp
- clean up spec

* Mon Jun 10 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-2jpp
- use sed instead of bash 2.x extension in link area to make spec compatible
  with distro using bash 1.1x

* Fri Jun 07 2002 Henri Gomez <hgomez@users.sourceforge.net> 1.0-1jpp 
- 1.0 (cvs 20020606)
- added short names in _javadir, as does jakarta developpers
- first jPackage release
