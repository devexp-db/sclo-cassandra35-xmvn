Name:           xmvn
Version:        0.2.3
Release:        1%{?dist}
Summary:        Local Extensions for Apache Maven
Group:          Development/Libraries
License:        ASL 2.0
URL:            http://mizdebsk.fedorapeople.org/xmvn
BuildArch:      noarch
Source0:        https://fedorahosted.org/released/%{name}/%{name}-%{version}.tar.xz

BuildRequires:  jpackage-utils
BuildRequires:  maven
BuildRequires:  plexus-classworlds

Requires:       jpackage-utils
Requires:       maven
Requires:       plexus-classworlds

%description
This package provides extensions for Apache Maven that can be used to
manage system artifact repository and use it to resolve Maven
artifacts in offline mode, as well as Maven plugins to help with
creating RPM packages containing Maven artifacts.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Documentation
Requires:       jpackage-utils

%description    javadoc
This package provides %{summary}.

%prep
%setup -q

%build
mvn-rpmbuild verify javadoc:aggregate

%install
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -d -m 755 %{buildroot}%{_javadir}/%{name}
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}

# POMs, JARs, depmaps
for dir in $(find -name pom.xml -exec dirname {} \;); do
    pushd $dir
    aid=$(sed -n '/^  <artifactId/{s/[^>]*>//;s/<.*//;p}' pom.xml)
    install -p -m 644 pom.xml %{buildroot}%{_mavenpomdir}/JPP.%{name}-${aid}.pom
    if [ -f target/*.jar ]; then
        install -p -m 644 target/*.jar %{buildroot}%{_javadir}/%{name}/${aid}.jar
        %add_maven_depmap JPP.%{name}-${aid}.pom %{name}/${aid}.jar
    else
        %add_maven_depmap JPP.%{name}-${aid}.pom
    fi
    popd
done

# API documentation
cp -pr target/site/apidocs/* %{buildroot}%{_javadocdir}/%{name}

# /usr/bin/xmvn script
%jpackage_script org.fedoraproject.maven.Launcher "" "" %{name}/%{name}-launcher:plexus/classworlds %{name} false

# /usr/bin/xmvn-resolve script
%jpackage_script org.fedoraproject.maven.tools.resolver.ResolverCli "" "" %{name}/%{name}-core:%{name}/%{name}-resolve %{name}-resolve true


%files
%doc LICENSE NOTICE
%doc AUTHORS README
%{_bindir}/*
%{_mavenpomdir}/*
%{_javadir}/%{name}
%{_mavendepmapfragdir}/%{name}

%files javadoc
%doc LICENSE NOTICE
%{_javadocdir}/%{name}

%changelog
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
