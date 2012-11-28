Name:           xmvn
Version:        0
Release:        2%{?dist}
Summary:        Local Extensions for Apache Maven
Group:          Development/Libraries
License:        ASL 2.0
URL:            http://mizdebsk.fedorapeople.org/xmvn
BuildArch:      noarch
Source0:        http://mizdebsk.fedorapeople.org/xmvn/%{name}-%{version}.tar.xz

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
* Wed Nov 28 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0-2
- Add jpackage scripts

* Mon Nov  5 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 0-1
- Initial packaging
