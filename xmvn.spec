Name:           xmvn
Version:        0.5.0
Release:        5%{?dist}
Summary:        Local Extensions for Apache Maven
License:        ASL 2.0
URL:            http://mizdebsk.fedorapeople.org/xmvn
BuildArch:      noarch
Source0:        https://fedorahosted.org/released/%{name}/%{name}-%{version}.tar.xz

# from upstream commit ccc197d to fix NPE
Patch0:         0001-Be-careful-when-unboxing-Boolean-that-can-be-null.patch

# from upstream commits f62ca1f and f6b2c9 to fix handling of packages with dots
# in groupid
Patch1:         0002-Implement-desired-handling-dots-in-JPP-groupId.patch


BuildRequires:  maven-local
BuildRequires:  beust-jcommander
BuildRequires:  cglib
BuildRequires:  guava
BuildRequires:  plexus-classworlds
BuildRequires:  plexus-containers-container-default
BuildRequires:  plexus-utils
BuildRequires:  xbean
BuildRequires:  xml-commons-apis
BuildRequires:  maven-dependency-plugin
BuildRequires:  maven-plugin-build-helper
BuildRequires:  maven-assembly-plugin

Requires:       maven
Requires:       beust-jcommander
Requires:       guava
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
%setup -q
%patch0 -p1
%patch1 -p1

# Add cglib test dependency as a workaround for rhbz#911365
%pom_add_dep cglib:cglib::test %{name}-core


# remove dependency plugin, we provide apache-maven by symlink
%pom_remove_plugin :maven-dependency-plugin
# get mavenVersion that is expected
mver=$(sed -n '/<mavenVersion>/{s/.*>\(.*\)<.*/\1/;p}' \
           xmvn-parent/pom.xml)
mkdir -p target/dependency/
ln -s %{_datadir}/maven target/dependency/apache-maven-$mver

%build
%mvn_file ":{xmvn-{core,connector}}" %{name}/@1 %{_datadir}/%{name}/lib/@1
%mvn_build -X

# let's use generated tarball to copy directory structure
# workaround for plexus-archiver bug
# https://github.com/sonatype/plexus-archiver/pull/9
sed -i '1s:^BZBZ:BZ:' target/*tar.bz2
tar --delay-directory-restore -xvf target/*tar.bz2
chmod -R +rwX %{name}-%{version}*


%install
%mvn_install

cp -r %{name}-%version/* %{buildroot}%{_datadir}/%{name}/
ln -sf %{_datadir}/maven/bin/mvn %{buildroot}%{_datadir}/%{name}/bin/mvn
ln -sf %{_datadir}/maven/bin/mvnDebug %{buildroot}%{_datadir}/%{name}/bin/mvnDebug
ln -sf %{_datadir}/maven/bin/mvnyjp %{buildroot}%{_datadir}/%{name}/bin/mvnyjp



# helper scripts
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 xmvn-tools/src/main/bin/tool-script \
               %{buildroot}%{_datadir}/%{name}/bin/

for tool in subst resolve bisect;do
    rm %{buildroot}%{_datadir}/%{name}/bin/%{name}-$tool
    ln -s tool-script \
          %{buildroot}%{_datadir}/%{name}/bin/%{name}-$tool

    cat <<EOF >%{buildroot}%{_bindir}/%{name}-$tool
#!/bin/sh -e
exec %{_datadir}/%{name}/bin/%{name}-$tool "\${@}"
EOF
    chmod +x %{buildroot}%{_bindir}/%{name}-$tool
done

# copy over maven lib directory
cp -r %{_datadir}/maven/lib/* %{buildroot}%{_datadir}/%{name}/lib/

# possibly recreate symlinks that can be automated with xmvn-subst
%{buildroot}%{_datadir}/%{name}/bin/%{name}-subst \
        %{buildroot}%{_datadir}/%{name}/

# /usr/bin/xmvn script
cat <<EOF >%{buildroot}%{_bindir}/%{name}
#!/bin/sh -e
export M2_HOME="\${M2_HOME:-%{_datadir}/%{name}}"
exec mvn "\${@}"
EOF

# make sure our conf is identical to maven so yum won't freak out
cp -P %{_datadir}/maven/conf/settings.xml %{buildroot}%{_datadir}/%{name}/conf/

%pretrans -p <lua>
-- we changed symlink to dir in 0.5.0-1, workaround RPM issues
for key, dir in pairs({"conf", "boot"}) do
    path = "%{_datadir}/%{name}/" .. dir
    if posix.readlink(path) then
       os.remove(path)
    end
end

%files -f .mfiles
%doc LICENSE NOTICE
%doc AUTHORS README
%attr(755,-,-) %{_bindir}/*
%{_datadir}/%{name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.5.0-5
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

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
