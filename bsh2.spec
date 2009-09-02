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

%define gcj_support 1
%define orig_name bsh
%define Name      BeanShell
%define fversion  2.0b4

%define section   free

Name:           bsh2
Version:        2.0
Release:        %mkrel 2.b4.2.0.2
Epoch:          0
Summary:        Lightweight Scripting for Java
License:        LGPL
Url:            http://www.beanshell.org/
Source0:        http://www.beanshell.org/bsh-2.0b4-src.jar
Source1:        beanshell-2.0b4.pom
Source2:        bsh-classpath-2.0b4.pom
Source3:        bsh-commands-2.0b4.pom
Source4:        bsh-core-2.0b4.pom
Source5:        bsh-reflect-2.0b4.pom
Source6:        bsh-util-2.0b4.pom
Source7:        bsh-bsf-2.0b4.pom
Source8:        bsh-classgen-2.0b4.pom
Patch1:         %{name}-asm.patch
Patch2:         %{name}-ClassGeneratorUtil.patch
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2
Requires:  jpackage-utils >= 0:1.7.2
Requires:  asm >= 0:1.5.3
Requires:  bsf

BuildRequires:  ant
BuildRequires:  asm >= 0:1.5.3
BuildRequires:  bsf
BuildRequires:  asm-javadoc
BuildRequires:  bsf-javadoc
BuildRequires:  java-rpmbuild
BuildRequires:  jpackage-utils >= 0:1.7.2
#BuildRequires:  libreadline-java
Group:          Development/Java
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%if ! %{gcj_support}
BuildArch:      noarch
%endif

Buildroot:      %{_tmppath}/%{name}-%{version}-buildroot

%description
BeanShell is a small, free, embeddable, Java source interpreter with
object scripting language features, written in Java. BeanShell executes
standard Java statements and expressions, in addition to obvious
scripting commands and syntax. BeanShell supports scripted objects as
simple method closures like those in Perl and JavaScript(tm).
You can use BeanShell interactively for Java experimentation and
debugging or as a simple scripting engine for your applications. In
short: BeanShell is a dynamically interpreted Java, plus some useful
stuff. Another way to describe it is to say that in many ways BeanShell
is to Java as Tcl/Tk is to C: BeanShell is embeddable - You can call
BeanShell from your Java applications to execute Java code dynamically
at run-time or to provide scripting extensibility for your applications.
Alternatively, you can call your Java applications and objects from
BeanShell; working with Java objects and APIs dynamically. Since
BeanShell is written in Java and runs in the same space as your
application, you can freely pass references to "real live" objects into
scripts and return them as results.

%package bsf
Summary:        BSF support for %{name}
Group:          Development/Java
Requires:       bsf

%description bsf
BSF support for %{name}.

%package classgen
Summary:        ASM support for %{name}
Group:          Development/Java
Requires:       asm

%description classgen
ASM support for %{name}.

%package manual
Summary:        Manual for %{name}
Group:          Development/Java

%description manual
Documentation for %{name}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
Javadoc for %{name}.

%package demo
Summary:        Demos for %{name}
Group:          Development/Java
AutoReqProv:    no

%description demo
Demonstrations and samples for %{name}.

%prep
%setup -q -n %{Name}-%{fversion}
%patch1 -p1
%patch2 -p0

for j in $(find . -name "*.jar"); do
    mv $j $j.no
done
mv tests/test-scripts/Data/addedCommand.jar.no tests/test-scripts/Data/addedCommand.jar
mv tests/test-scripts/Data/addclass.jar.no tests/test-scripts/Data/addclass.jar

%build
pushd lib
ln -sf $(build-classpath asm/asm)
ln -sf $(build-classpath bsf)
ln -sf $(build-classpath servlet)
popd

# set VERSION
%__perl -p -i -e 's|VERSION =.*;|VERSION = "%{version}-%{release}";|' src/bsh/Interpreter.java

# remove internal asm code, use JPackage external jar instead
%__rm -rf src/bsh/org
%__perl -p -i -e 's|bsh.org.objectweb.asm|org.objectweb.asm|' src/bsh/ClassGeneratorUtil.java
export CLASSPATH=$(build-classpath ant-launcher)
%ant -Dasm.javadoc=%{_javadocdir}/asm \
     -Dbsf.javadoc=%{_javadocdir}/bsf \
     -Djava.javadoc=%{_javadocdir}/java \
     dist test
(cd docs/faq && %ant)
(cd docs/manual && %ant)

%install
%__rm -rf %{buildroot}

# jars
%__mkdir_p %{buildroot}%{_javadir}/%{name}
#rap#%__rm -f dist/%{orig_name}-%{fversion}.jar
%__rm -f dist/%{orig_name}-%{fversion}-src.jar
for jar in dist/*.jar; do
  %__install -m 644 ${jar} %{buildroot}%{_javadir}/%{name}/`basename ${jar} -%{fversion}.jar`-%{version}.jar
done
(cd %{buildroot}%{_javadir}/%{name} && for jar in *-%{version}*; do %__ln_s ${jar} ${jar/-%{version}/}; done)

%add_to_maven_depmap org.beanshell beanshell %{fversion} JPP/%{name} bsh
%add_to_maven_depmap org.beanshell bsh %{fversion} JPP/%{name} bsh
%add_to_maven_depmap org.beanshell bsh-classpath %{fversion} JPP/%{name} bsh-classpath
%add_to_maven_depmap org.beanshell bsh-commands %{fversion} JPP/%{name} bsh-commands
%add_to_maven_depmap org.beanshell bsh-core %{fversion} JPP/%{name} bsh-core
%add_to_maven_depmap org.beanshell bsh-reflect %{fversion} JPP/%{name} bsh-reflect
%add_to_maven_depmap org.beanshell bsh-util %{fversion} JPP/%{name} bsh-util
%add_to_maven_depmap org.beanshell bsh-bsf %{fversion} JPP/%{name} bsh-bsf
%add_to_maven_depmap org.beanshell bsh-classgen %{fversion} JPP/%{name} bsh-classgen

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh.pom
install -pm 644 %{SOURCE2} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-classpath.pom
install -pm 644 %{SOURCE3} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-commands.pom
install -pm 644 %{SOURCE4} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-core.pom
install -pm 644 %{SOURCE5} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-reflect.pom
install -pm 644 %{SOURCE6} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-util.pom
install -pm 644 %{SOURCE7} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-bsf.pom
install -pm 644 %{SOURCE8} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}-bsh-classgen.pom

# manual
find docs -name ".cvswrappers" -exec %__rm -f {} \;
find docs -name "*.xml" -exec %__rm -f {} \;
find docs -name "*.xsl" -exec %__rm -f {} \;
find docs -name "*.log" -exec %__rm -f {} \;
(cd docs/manual && %__mv -f html/* .)
(cd docs/manual && %__rm -rf html)
(cd docs/manual && %__rm -rf xsl)

# javadoc
%__mkdir_p %{buildroot}%{_javadocdir}/%{name}-%{version}
%__cp -a javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
(cd %{buildroot}%{_javadocdir} && %__ln_s %{name}-%{version} %{name})

# demo
for i in `find tests -name "*.bsh"`; do
  %__perl -p -i -e 's,^\n?#!(/(usr/)?bin/java bsh\.Interpreter|/bin/sh),#!%{_bindir}/%{name},' $i
done

%__mkdir_p %{buildroot}%{_datadir}/%{name}
%__cp -a tests %{buildroot}%{_datadir}/%{name}

find %{buildroot}%{_datadir}/%{name} -type d \
  | sed 's|'%{buildroot}'|%dir |' >  %{name}-demo-%{version}.files
find %{buildroot}%{_datadir}/%{name} -type f -name "*.bsh" \
  | sed 's|'%{buildroot}'|%attr(0755,root,root) |'      >> %{name}-demo-%{version}.files
find %{buildroot}%{_datadir}/%{name} -type f ! -name "*.bsh" \
  | sed 's|'%{buildroot}'|%attr(0644,root,root) |'      >> %{name}-demo-%{version}.files

# bshservlet
%__mkdir_p %{buildroot}%{_datadir}/%{name}/bshservlet
(cd %{buildroot}%{_datadir}/%{name}/bshservlet
jar xf $RPM_BUILD_DIR/%{Name}-%{fversion}/dist/bshservlet.war
)

# scripts
%__mkdir_p %{buildroot}%{_bindir}

%__cat > %{buildroot}%{_bindir}/%{name} << EOF
#!/bin/sh
#
# %{name} script
# JPackage Project (http://jpackage.sourceforge.net)

# Source functions library
. %{_datadir}/java-utils/java-functions

# Source system prefs
if [ -f %{_sysconfdir}/%{name}.conf ] ; then
  . %{_sysconfdir}/%{name}.conf
fi

# Source user prefs
if [ -f \$HOME/.%{name}rc ] ; then
  . \$HOME/.%{name}rc
fi

# Configuration
MAIN_CLASS=bsh.Interpreter
if [ -n "\$BSH_DEBUG" ]; then
  BASE_FLAGS=-Ddebug=true
fi

BASE_JARS="%{name}.jar"

#if [ -f /usr/lib/libJavaReadline.so ]; then
#  BASE_FLAGS="$BASE_FLAGS -Djava.library.path=/usr/lib"
#  BASE_FLAGS="\$BASE_FLAGS -Dbsh.console.readlinelib=GnuReadline"
#  BASE_JARS="\$BASE_JARS libreadline-java.jar"
#fi

# Set parameters
set_jvm
set_classpath \$BASE_JARS
set_flags \$BASE_FLAGS
set_options \$BASE_OPTIONS

# Let's start
run "\$@"
EOF

%__cat > %{buildroot}%{_bindir}/%{name}doc << EOF
#!/usr/bin/env %{_bindir}/%{name}
EOF
%__cat scripts/bshdoc.bsh >> %{buildroot}%{_bindir}/%{name}doc

%if %{gcj_support}
export CLASSPATH=$(build-classpath gnu-crypto)
%{_bindir}/aot-compile-rpm \
--exclude %{_datadir}/%{name}/tests/test-scripts/Data/addedCommand.jar \
--exclude %{_datadir}/%{name}/tests/test-scripts/Data/addclass.jar

%endif

%clean
%__rm -rf %{buildroot}
%__rm -rf $RPM_BUILD_DIR/META-INF

%post
%update_maven_depmap
%if %{gcj_support}
%{update_gcjdb}
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
%{clean_gcjdb}
%endif

%files
%defattr(0644,root,root,0755)
%attr(0755,root,root) %{_bindir}/%{name}
%attr(0755,root,root) %{_bindir}/%{name}doc
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/%{orig_name}-%{version}.jar
%{_javadir}/%{name}/%{orig_name}.jar
%{_javadir}/%{name}/%{orig_name}-classpath*.jar
%{_javadir}/%{name}/%{orig_name}-commands*.jar
%{_javadir}/%{name}/%{orig_name}-core*.jar
%{_javadir}/%{name}/%{orig_name}-reflect*.jar
%{_javadir}/%{name}/%{orig_name}-util*.jar
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/bshservlet
%{_datadir}/maven2/poms/*
%{_mavendepmapfragdir}
%if %{gcj_support}
%dir %attr(-,root,root) %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/bsh-*%{version}.jar.*
%endif

%files bsf
%defattr(0644,root,root,0755)
%{_javadir}/%{name}/%{orig_name}-bsf*.jar

%files classgen
%defattr(0644,root,root,0755)
%{_javadir}/%{name}/%{orig_name}-classgen*.jar

%files manual
%defattr(0644,root,root,0755)
%doc docs/*

%files javadoc
%defattr(0644,root,root,0755)
%dir %{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}-%{version}/*
%dir %{_javadocdir}/%{name}

%files demo -f %{name}-demo-%{version}.files
%defattr(0644,root,root,0755)
