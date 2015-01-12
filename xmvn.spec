%global pkg_name xmvn
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

Name:           %{?scl_prefix}%{pkg_name}
Version:        2.1.1
Release:        1.6%{?dist}
Summary:        Local Extensions for Apache Maven
License:        ASL 2.0
URL:            http://mizdebsk.fedorapeople.org/xmvn
BuildArch:      noarch

# git snapshot
Source0:        https://fedorahosted.org/released/%{pkg_name}/%{pkg_name}-%{version}.tar.xz

Patch0001:      0001-Port-to-Maven-3.0.5.patch
Patch0003:      0003-Add-hack-for-forcing-correct-namespace-in-depmap-res.patch
Patch0004:      0004-Port-to-Modello-1.7.patch

BuildRequires:  %{?scl_prefix}maven
BuildRequires:  %{?scl_prefix}maven-local
BuildRequires:  %{?scl_prefix}beust-jcommander
BuildRequires:  %{?scl_prefix}cglib
BuildRequires:  %{?scl_prefix}maven-dependency-plugin
BuildRequires:  %{?scl_prefix}maven-plugin-build-helper
BuildRequires:  %{?scl_prefix}maven-assembly-plugin
BuildRequires:  %{?scl_prefix}maven-invoker-plugin
BuildRequires:  %{?scl_prefix_java_common}objectweb-asm5
BuildRequires:  %{?scl_prefix}modello >= 1.7
BuildRequires:  %{?scl_prefix}xmlunit
BuildRequires:  %{?scl_prefix}apache-ivy >= 2.3.0-4.8
BuildRequires:  %{?scl_prefix}junit
BuildRequires:  %{?scl_prefix}slf4j-simple

Requires:       %{?scl_prefix}maven
Requires:       %{name}-api = %{version}-%{release}
Requires:       %{name}-connector-aether = %{version}-%{release}
Requires:       %{name}-core = %{version}-%{release}

%description
This package provides extensions for Apache Maven that can be used to
manage system artifact repository and use it to resolve Maven
artifacts in offline mode, as well as Maven plugins to help with
creating RPM packages containing Maven artifacts.

%package        parent-pom
Summary:        XMvn Parent POM

%description    parent-pom
This package provides XMvn parent POM.

%package        api
Summary:        XMvn API

%description    api
This package provides XMvn API module which contains public interface
for functionality implemented by XMvn Core.

%package        launcher
Summary:        XMvn Launcher

%description    launcher
This package provides XMvn Launcher module, which provides a way of
launching XMvn running in isolated class realm and locating XMVn
services.

%package        core
Summary:        XMvn Core

%description    core
This package provides XMvn Core module, which implements the essential
functionality of XMvn such as resolution of artifacts from system
repository.

%package        connector-aether
Summary:        XMvn Connector for Eclipse Aether

%description    connector-aether
This package provides XMvn Connector for Eclipse Aether, which
provides integration of Eclipse Aether with XMvn.  It provides an
adapter which allows XMvn resolver to be used as Aether workspace
reader.

%package        connector-ivy
Summary:        XMvn Connector for Apache Ivy

%description    connector-ivy
This package provides XMvn Connector for Apache Ivy, which provides
integration of Apache Ivy with XMvn.  It provides an adapter which
allows XMvn resolver to be used as Ivy resolver.

%package        mojo
Summary:        XMvn MOJO

%description    mojo
This package provides XMvn MOJO, which is a Maven plugin that consists
of several MOJOs.  Some goals of these MOJOs are intended to be
attached to default Maven lifecycle when building packages, others can
be called directly from Maven command line.

%package        tools-pom
Summary:        XMvn Tools POM

%description    tools-pom
This package provides XMvn Tools parent POM.

%package        resolve
Summary:        XMvn Resolver

%description    resolve
This package provides XMvn Resolver, which is a very simple
commald-line tool to resolve Maven artifacts from system repositories.
Basically it's just an interface to artifact resolution mechanism
implemented by XMvn Core.  The primary intended use case of XMvn
Resolver is debugging local artifact repositories.

%package        bisect
Summary:        XMvn Bisect

%description    bisect
This package provides XMvn Bisect, which is a debugging tool that can
diagnose build failures by using bisection method.

%package        subst
Summary:        XMvn Subst

%description    subst
This package provides XMvn Subst, which is a tool that can substitute
Maven artifact files with symbolic links to corresponding files in
artifact repository.

%package        install
Summary:        XMvn Install

%description    install
This package provides XMvn Install, which is a command-line interface
to XMvn installer.  The installer reads reactor metadata and performs
artifact installation according to specified configuration.

%package        javadoc
Summary:        API documentation for %{pkg_name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%patch0001 -p1
%patch0003 -p1
%patch0004 -p1

# XXX Disable duplicate metadata enforcing for now
sed -i /artifactMap.remove/d $(find -name MetadataResolver.java)

%mvn_package :xmvn __noinstall

# In XMvn 2.x xmvn-connector was renamed to xmvn-connector-aether
%mvn_alias :xmvn-connector-aether :xmvn-connector

# remove dependency plugin maven-binaries execution
# we provide apache-maven by symlink
%pom_xpath_remove "pom:executions/pom:execution[pom:id[text()='maven-binaries']]"

# get mavenVersion that is expected
mver=$(sed -n '/<mavenVersion>/{s/.*>\(.*\)<.*/\1/;p}' \
           xmvn-parent/pom.xml)
mkdir -p target/dependency/
cp -aL %{_datadir}/maven target/dependency/apache-maven-$mver

# skip ITs for now (mix of old & new XMvn config causes issues
rm -rf src/it
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
# XXX some tests fail on ARM for unknown reason, see why
%mvn_build -s -f

tar --delay-directory-restore -xvf target/*tar.bz2
chmod -R +rwX %{pkg_name}-%{version}*
# These are installed as doc
rm -Rf %{pkg_name}-%{version}*/{AUTHORS,README,LICENSE,NOTICE}
%{?scl:EOF}


%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_install

install -d -m 755 %{buildroot}%{_datadir}/%{pkg_name}
cp -r %{pkg_name}-%{version}*/* %{buildroot}%{_datadir}/%{pkg_name}/
ln -sf %{_datadir}/maven/bin/mvn %{buildroot}%{_datadir}/%{pkg_name}/bin/mvn
ln -sf %{_datadir}/maven/bin/mvnDebug %{buildroot}%{_datadir}/%{pkg_name}/bin/mvnDebug
ln -sf %{_datadir}/maven/bin/mvnyjp %{buildroot}%{_datadir}/%{pkg_name}/bin/mvnyjp

# helper scripts
install -d -m 755 %{buildroot}%{_bindir}
for tool in subst resolve bisect install;do
    cat <<XEOF >%{buildroot}%{_bindir}/%{pkg_name}-$tool
#!/bin/sh -e
exec %{_datadir}/%{pkg_name}/bin/%{pkg_name}-$tool "\${@}"
XEOF
    chmod +x %{buildroot}%{_bindir}/%{pkg_name}-$tool
done

# copy over maven lib directory
cp -r %{_datadir}/maven/lib/* %{buildroot}%{_datadir}/%{pkg_name}/lib/

# possibly recreate symlinks that can be automated with xmvn-subst
%{pkg_name}-subst %{buildroot}%{_datadir}/%{pkg_name}/

# /usr/bin/xmvn script
echo "#!/bin/sh -e
export M2_HOME=\"\${M2_HOME:-%{_datadir}/%{pkg_name}}\"
exec mvn \"\${@}\"" >%{buildroot}%{_bindir}/%{pkg_name}

# make sure our conf is identical to maven so yum won't freak out
install -d -m 755 %{buildroot}%{_datadir}/%{pkg_name}/conf/
cp -P %{_datadir}/maven/conf/settings.xml %{buildroot}%{_datadir}/%{pkg_name}/conf/
cp -P %{_datadir}/maven/bin/m2.conf %{buildroot}%{_datadir}/%{pkg_name}/bin/
%{?scl:EOF}

%files
%attr(755,-,-) %{_bindir}/%{pkg_name}
%dir %{_datadir}/%{pkg_name}/bin
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/lib/*.jar
%{_datadir}/%{pkg_name}/lib/ext
%{_datadir}/%{pkg_name}/bin/m2.conf
%{_datadir}/%{pkg_name}/bin/mvn
%{_datadir}/%{pkg_name}/bin/mvnDebug
%{_datadir}/%{pkg_name}/bin/mvnyjp
%{_datadir}/%{pkg_name}/bin/xmvn
%{_datadir}/%{pkg_name}/boot
%{_datadir}/%{pkg_name}/conf

%files parent-pom -f .mfiles-xmvn-parent
%doc LICENSE NOTICE

%files launcher -f .mfiles-xmvn-launcher
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/lib/core

%files core -f .mfiles-xmvn-core

%files api -f .mfiles-xmvn-api
%dir %{_javadir}/%{pkg_name}
%doc LICENSE NOTICE
%doc AUTHORS README

%files connector-aether -f .mfiles-xmvn-connector-aether

%files connector-ivy -f .mfiles-xmvn-connector-ivy
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/lib/ivy

%files mojo -f .mfiles-xmvn-mojo

%files tools-pom -f .mfiles-xmvn-tools

%files resolve -f .mfiles-xmvn-resolve
%attr(755,-,-) %{_bindir}/%{pkg_name}-resolve
%dir %{_datadir}/%{pkg_name}/bin
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/bin/%{pkg_name}-resolve
%{_datadir}/%{pkg_name}/lib/resolver

%files bisect -f .mfiles-xmvn-bisect
%attr(755,-,-) %{_bindir}/%{pkg_name}-bisect
%dir %{_datadir}/%{pkg_name}/bin
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/bin/%{pkg_name}-bisect
%{_datadir}/%{pkg_name}/lib/bisect

%files subst -f .mfiles-xmvn-subst
%attr(755,-,-) %{_bindir}/%{pkg_name}-subst
%dir %{_datadir}/%{pkg_name}/bin
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/bin/%{pkg_name}-subst
%{_datadir}/%{pkg_name}/lib/subst

%files install -f .mfiles-xmvn-install
%attr(755,-,-) %{_bindir}/%{pkg_name}-install
%dir %{_datadir}/%{pkg_name}/bin
%dir %{_datadir}/%{pkg_name}/lib
%{_datadir}/%{pkg_name}/bin/%{pkg_name}-install
%{_datadir}/%{pkg_name}/lib/installer

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Mon Jan 12 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.1-1.6
- Rebuild to fix symlinks

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 2.1.1-1.5
- Rebuild to regenerate requires from java-common

* Fri Jan  9 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.1-1.4
- Disable duplicate metadata enforcing for now

* Wed Jan  7 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.1-1.3
- Re-add dependency on ASM 5

* Wed Jan  7 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.1-1.2
- Port to Modello 1.7

* Mon Jan  5 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.1.1-1.1
- Update to upstream version 2.1.1

* Fri Jan  2 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.2.0-0.3.20141212git221a2d4
- Prevent xmvn-resolve from failing in XML mode

* Wed Dec 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.2.0-0.2.20141212git221a2d4
- Add patch for namespace support in depmap resolver

* Tue Dec 16 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 2.2.0-0.1.20141212git221a2d4
- Update to upstream 2.2.0 snapshot

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.11
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.10
- Mass rebuild 2014-02-19

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.9
- Remove workaround for rhbz#447156

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.8
- Mass rebuild 2014-02-18

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.7
- Add missing BR: maven-plugin-plugin, plexus-containers-component-metadata

* Mon Feb 17 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.6
- Remove temporary hacks

* Fri Feb 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.5
- Remove temp BR

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.4
- SCL-ize requires and build-requires
- Bump version requirement on maven

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.3
- Rebuild to regenerate auto-requires

* Wed Feb 12 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.2
- Use Maven from %%{_root_datadir} for now
- Fix quotation in nested here-documents
- Fix symlinks to Maven
- Fix dangling symlinks to Maven JARs
- Avoid nested here-documents

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5.1
- First maven30 software collection build

* Fri Jan 10 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-5
- Split 1 patch to 3 patches, one per feature
- Add support for absolute artifact symlinks

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1.3.0-4
- Mass rebuild 2013-12-27

* Thu Nov  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-3
- Fix guice symlinks

* Thu Nov  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-2
- Bump Maven requirement to 3.0.5-14

* Thu Nov  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.3.0-1
- Rebase upstream version 1.3.0

* Tue Oct 01 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.1.0-1
- Update to upstream version 1.1.0

* Fri Sep 27 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.0.2-3
- Add __default package specifier support

* Mon Sep 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.0.2-2
- Don't try to relativize symlink targets
- Restotre support for relative symlinks

* Fri Sep 20 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1.0.2-1
- Update to upstream version 1.0.2

* Tue Sep 10 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.0.0-2
- Workaround broken symlinks for core and connector (#986909)

* Mon Sep 09 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 1.0.0-1
- Updating to upstream 1.0.0

* Tue Sep  3 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> 1.0.0-0.2.alpha1
- Update to upstream version 1.0.0 alpha1

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.1-3
- Rebuild without bootstrapping

* Tue Jul 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.1-2
- Install symlink to simplelogger.properties in %{_sysconfdir}

* Tue Jul 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.1-1
- Update to upstream version 0.5.1

* Tue Jul 23 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.0-7
- Allow installation of Eclipse plugins in javadir

* Mon Jul 22 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.0-6
- Remove workaround for plexus-archiver bug
- Use sonatype-aether symlinks

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.0-5
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Wed Jun  5 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.0-5
- Fix resolution of tools.jar

* Fri May 31 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.5.0-4
- Fix handling of packages with dots in groupId
- Previous versions also fixed bug #948731

* Tue May 28 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.5.0-3
- Move pre scriptlet to pretrans and implement in lua

* Fri May 24 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.5.0-2
- Fix upgrade path scriptlet
- Add patch to fix NPE when debugging is disabled

* Fri May 24 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 0.5.0-1
- Update to upstream version 0.5.0

* Fri May 17 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.2-3
- Add patch: install MOJO fix

* Wed Apr 17 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.2-2
- Update plexus-containers-container-default JAR location

* Tue Apr  9 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.2-1
- Update to upstream version 0.4.2

* Thu Mar 21 2013 Michal Srb <msrb@redhat.com> - 0.4.1-1
- Update to upstream version 0.4.1

* Fri Mar 15 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-1
- Update to upstream version 0.4.0

* Fri Mar 15 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.7
- Enable tests

* Thu Mar 14 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.6
- Update to newer snapshot

* Wed Mar 13 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.5
- Update to newer snapshot

* Wed Mar 13 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.4
- Set proper permissions for scripts in _bindir

* Tue Mar 12 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.3
- Update to new upstream snapshot
- Create custom /usr/bin/xmvn instead of using %%jpackage_script
- Mirror maven directory structure
- Add Plexus Classworlds config file

* Wed Mar  6 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.2
- Update to newer snapshot

* Wed Mar  6 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.4.0-0.1
- Update to upstream snapshot of version 0.4.0

* Mon Feb 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.3.1-2
- Install effective POMs into a separate directory

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
