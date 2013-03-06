Name:           xmvn
Version:        0.4.0
Release:        0.1%{?dist}
Summary:        Local Extensions for Apache Maven
License:        ASL 2.0
URL:            http://mizdebsk.fedorapeople.org/xmvn
BuildArch:      noarch
Source0:        http://mizdebsk.fedorapeople.org/%{name}/%{name}-snapshot.tar.xz

BuildRequires:  maven-local
BuildRequires:  beust-jcommander
BuildRequires:  guava
BuildRequires:  plexus-classworlds
BuildRequires:  plexus-classworlds
BuildRequires:  plexus-containers-container-default
BuildRequires:  plexus-utils
BuildRequires:  xbean
BuildRequires:  xml-commons-apis

Requires:       maven
Requires:       beust-jcommander
Requires:       guava
Requires:       plexus-classworlds
Requires:       plexus-classworlds
Requires:       plexus-containers-container-default
Requires:       plexus-utils
Requires:       xbean
Requires:       xml-commons-apis

%description
This package provides extensions for Apache Maven that can be used to
manage system artifact repository and use it to resolve Maven
artifacts in offline mode, as well as Maven plugins to help with
creating RPM packages containing Maven artifacts.

%package        javadoc
Summary:        API documentation for %{name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -q -n %{name}-snapshot

%build
%mvn_file ":{xmvn-{core,connector}}" %{name}/@1 %{_datadir}/%{name}/lib/@1
%mvn_build -f

%install
%mvn_install

# /usr/bin/xmvn script
%jpackage_script org.fedoraproject.maven.Launcher "" "" %{name}/%{name}-launcher:plexus/classworlds %{name} false

# /usr/bin/xmvn-resolve script
%jpackage_script org.fedoraproject.maven.tools.resolver.ResolverCli "" "" %{name}/%{name}-core:%{name}/%{name}-resolve:beust-jcommander:xml-commons-apis:plexus/containers-container-default:plexus/classworlds:plexus/utils:xbean/xbean-reflect:guava %{name}-resolve true


%files -f .mfiles
%doc LICENSE NOTICE
%doc AUTHORS README
%{_bindir}/*
%{_datadir}/%{name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Wed Mar  6 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.1
- Update to upstream snapshot of version 0.4.0

* Thu Feb  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.3.1-1
- Update to upstream version 0.3.1

* Tue Feb  5 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.3.0-1
- Update to upstream version 0.3.0
- Don't rely on JPP symlinks when resolving artifacts
- Blacklist more artifacts
- Fix dependencies

* Thu Jan 24 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.6-1
- Update to upstream version 0.2.6

* Mon Jan 21 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.5-1
- Update to upstream version 0.2.5

* Fri Jan 11 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.4-1
- Update to upstream version 0.2.4

* Wed Jan  9 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.3-1
- Update to upstream version 0.2.3

* Tue Jan  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.2-1
- Update to upstream version 0.2.2

* Tue Jan  8 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.1-1
- Update to upstream version 0.2.1

* Mon Jan  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.2.0-1
- Update to upstream version 0.2.0
- New major features: depmaps, compat symlinks, builddep MOJO
- Install effective POMs for non-POM artifacts
- Multiple major and minor bugfixes
- Drop support for resolving artifacts from %%_javajnidir

* Fri Dec  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.5-1
- Update to upstream version 0.1.5

* Fri Dec  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.4-1
- Update to upstream version 0.1.4

* Fri Dec  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.3-1
- Update to upstream version 0.1.3

* Fri Dec  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.2-1
- Update to upstream version 0.1.2

* Fri Dec  7 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.1-1
- Update to upstream version 0.1.1

* Thu Dec  6 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.1.0-1
- Update to upstream version 0.1.0
- Implement auto requires generator

* Mon Dec  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.0.2-1
- Update to upstream version 0.0.2

* Thu Nov 29 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.0.1-1
- Update to upstream version 0.0.1

* Wed Nov 28 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0-2
- Add jpackage scripts

* Mon Nov  5 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0-1
- Initial packaging
