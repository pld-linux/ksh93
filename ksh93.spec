Summary:	Original AT&T Korn Shell
Name:		ksh93
Version:	1.1
Release:	1
License:	AT&T Open Source
Group:		Applications/Shells
Group(de):	Applikationen/Shells
Group(pl):	Aplikacje/Pow³oki
Source0:	http://www.research.att.com/~gsf/download/tgz/INIT.2001-01-01.0000.tgz
Source1:	http://www.research.att.com/~gsf/download/tgz/ast-base.2001-01-01.0000.tgz
Source2:	%{name}-ldhack.sh
Patch0:		%{name}-build.patch
Patch1:		%{name}-echo-e.patch
URL:		http://www.kornshell.com/
BuildRequires:	glibc-static
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
KSH-93 is the most recent version of the KornShell Language described
in "The KornShell Command and Programming Language," by Morris Bolsky
and David Korn of AT&T Bell Laboratories, ISBN 0-13-182700-6. The
KornShell is a shell programming language, which is upward compatible
with "sh" (the Bourne Shell), and is intended to conform to the IEEE
P1003.2/ISO 9945.2 Shell and Utilities standard. KSH-93 provides an
enhanced programming environment in addition to the major
command-entry features of the BSD shell "csh". With KSH-93,
medium-sized programming tasks can be performed at shell-level without
a significant loss in performance. In addition, "sh" scripts can be
run on KSH-93 without modification.

%package static
Summary:	Staticly linked Korn Shell
Group:		Applications/Shells
Group(de):	Applikationen/Shells
Group(pl):	Aplikacje/Pow³oki
Requires:	%{name}

%description static
KSH-93 is the most recent version of the KornShell Language described
in "The KornShell Command and Programming Language," by Morris Bolsky
and David Korn of AT&T Bell Laboratories, ISBN 0-13-182700-6. The
KornShell is a shell programming language, which is upward compatible
with "sh" (the Bourne Shell), and is intended to conform to the IEEE
P1003.2/ISO 9945.2 Shell and Utilities standard. KSH-93 provides an
enhanced programming environment in addition to the major
command-entry features of the BSD shell "csh". With KSH-93,
medium-sized programming tasks can be performed at shell-level without
a significant loss in performance. In addition, "sh" scripts can be
run on KSH-93 without modification.

This packege contains staticly linked version of pdksh.

%prep
%setup -q -c -a1
%patch0 -p1
%patch1 -p1
install -m755 %{SOURCE2} ldhack.sh
touch lib/package/gen/ast.license.accepted
rm -f src/cmd/ksh93/Mamfile

%build
LC_ALL=POSIX; export LC_ALL

# Yes this sucks, but that's the way (I'm too lazy to fix this stuff)
CCFLAGS="%{rpmcflags}" LD="`pwd`/ldhack.sh" ./bin/package make ksh93 || :
CCFLAGS="%{rpmcflags}" LD="`pwd`/ldhack.sh" ./bin/package make ksh93 || :
CCFLAGS="%{rpmcflags}" LD="`pwd`/ldhack.sh" ./bin/package make ksh93

cd arch/*/src/cmd/ksh93
%{__cc} -o ksh93 pmain.o -L../../../lib -lksh \
	../../../lib/libdll.a -ldl ../../../lib/libcmd.a \
	../../../lib/libast.a -lm

%{__cc} -static -o ksh93.static pmain.o -L../../../lib -lksh \
	../../../lib/libdll.a -ldl ../../../lib/libcmd.a \
	../../../lib/libast.a -lm

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_mandir}/man1,/lib,/bin,%{_sysconfdir}}

install arch/*/src/cmd/ksh93/ksh93 $RPM_BUILD_ROOT/bin
install arch/*/src/cmd/ksh93/ksh93.static $RPM_BUILD_ROOT/bin
install arch/*/src/cmd/ksh93/libksh.so.* $RPM_BUILD_ROOT/lib
install arch/*/man/man1/sh.1 $RPM_BUILD_ROOT%{_mandir}/man1/ksh93.1

cp lib/package/LICENSES/ast LICENSE
gzip -9nf LICENSE

cd src/cmd/ksh93
mv -f OBSOLETE OBSOLETE.mm
groff -mm -Tascii OBSOLETE.mm > OBSOLETE
groff -mm -Tascii sh.memo > memo.txt
groff -mm -Tascii PROMO.mm > PROMO

gzip -9nf COMPATIBILITY README RELEASE* builtins.mm OBSOLETE memo.txt PROMO

%post
/sbin/ldconfig
if [ ! -f /etc/shells ]; then
	echo "/bin/ksh93" > /etc/shells
else
	while read SHNAME; do
        	if [ "$SHNAME" = "/bin/ksh93" ]; then
                	HAS_KSH=1
	        fi
	done < /etc/shells
	[ -n "$HAS_KSH" ] || echo "/bin/ksh93" >> /etc/shells
fi

%post static
if [ ! -f /etc/shells ]; then
	echo "/bin/ksh93.static" > /etc/shells
else
	while read SHNAME; do
        	if [ "$SHNAME" = "/bin/ksh93.static" ]; then
                	HAS_KSH_STATIC=1
	        fi
	done < /etc/shells
	[ -n "$HAS_KSH_STATIC" ] || echo "/bin/ksh93.static" >> /etc/shells
fi

%preun
if [ "$1" = "0" ]; then
	while read SHNAME; do
		[ "$SHNAME" = "/bin/ksh93" ] ||\
		echo "$SHNAME"
	done < /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi

%preun static
if [ "$1" = "0" ]; then
	while read SHNAME; do
		[ "$SHNAME" = "/bin/ksh93.static" ] ||\
		echo "$SHNAME"
	done
	mv -f /etc/shells.new /etc/shells
fi

%postun
/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc src/cmd/ksh93/*.gz LICENSE.gz

%attr(755,root,root) /bin/ksh93
%attr(755,root,root) /lib/libksh.so.*

%{_mandir}/man1/*

%{?bcond_off_static:#}%files static
%{?bcond_off_static:#}%defattr(644,root,root,755)
%{?bcond_off_static:#}%attr(755,root,root) /bin/ksh93.static

%clean
rm -rf $RPM_BUILD_ROOT
