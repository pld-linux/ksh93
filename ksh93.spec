#
# Conditional build:
%bcond_without		static		# don't build static version
%bcond_with		binsh		# build with /bin/sh symlink
#
Summary:	Original AT&T Korn Shell
Summary(pl):	Oryginalna pow³oka Korna z AT&T
Name:		ksh93
Version:	1.1
Release:	5
License:	AT&T Open Source
Group:		Applications/Shells
Source0:	http://www.research.att.com/~gsf/download/tgz/INIT.2001-01-01.0000.tgz
# Source0-md5:	799b061ff85c22e7efc9a3b9e610e5c6
Source1:	http://www.research.att.com/~gsf/download/tgz/ast-base.2001-01-01.0000.tgz
# Source1-md5:	9315343c62c278bfdcb155bca8316dd7
Source2:	%{name}-ldhack.sh
Patch0:		%{name}-build.patch
Patch1:		%{name}-echo-e.patch
Patch2:		%{name}-login.patch
URL:		http://www.kornshell.com/
%if %{with static}
BuildRequires:	glibc-static
%endif
Requires(post):	/sbin/ldconfig
Requires(preun):	fileutils
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

%description -l pl
KSH-93 jest naj¶wie¿sz± wersj± jêzyka KornShell opisanego przez
Morrisa Blolsky'ego i Davida Korna z AT&T Bell Laboratories. Pow³oka
Korna jest zgodna z "sh" (pow³ok± Bourne'a) i ma byæ zgodna z norm±
IEEE P1003.2/ISO 9945.2.

%package static
Summary:	Statically linked Korn Shell
Summary(pl):	Skonsolidowana statycznie pow³oka Korna
Group:		Applications/Shells
Requires:	%{name}
Requires(preun):	fileutils

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

This packege contains statically linked version of ksh93.

%description static -l pl
KSH-93 jest naj¶wie¿sz± wersj± jêzyka KornShell opisanego przez
Morrisa Blolsky'ego i Davida Korna z AT&T Bell Laboratories. Pow³oka
Korna jest zgodna z "sh" (pow³ok± Bourne'a) i ma byæ zgodna z norm±
IEEE P1003.2/ISO 9945.2.

Ten pakiet zawiera wersjê ksh93 skonsolidowan± statycznie.

%prep
%setup -q -c -a1
%patch0 -p1
%patch1 -p1
%patch2 -p1
install -m755 %{SOURCE2} ldhack.sh
touch lib/package/gen/ast.license.accepted
rm -f src/cmd/ksh93/Mamfile

# at some moment build stops using CCFLAGS - fix it:
cd src/cmd/nmake
sed -e 's@CC_OPTIMIZE=\$optimize@CC_OPTIMIZE="%{rpmcflags}"@' make.probe > make.probe.n
mv -f make.probe.n make.probe

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

%if %{with static}
%{__cc} -static -o ksh93.static pmain.o -L../../../lib -lksh \
	../../../lib/libdll.a -ldl ../../../lib/libcmd.a \
	../../../lib/libast.a -lm
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_mandir}/man1,/lib,/bin,%{_sysconfdir}}

install arch/*/src/cmd/ksh93/ksh93 $RPM_BUILD_ROOT/bin
%if %{with static}
install arch/*/src/cmd/ksh93/ksh93.static $RPM_BUILD_ROOT/bin
%endif
install arch/*/src/cmd/ksh93/libksh.so.* $RPM_BUILD_ROOT/lib
install arch/*/man/man1/sh.1 $RPM_BUILD_ROOT%{_mandir}/man1/ksh93.1

%if %{with binsh}
echo ".so ksh93.1" > $RPM_BUILD_ROOT%{_mandir}/man1/sh.1
ln -sf ksh93 $RPM_BUILD_ROOT/bin/sh
%endif

cp -f lib/package/LICENSES/ast LICENSE

cd src/cmd/ksh93
mv -f OBSOLETE OBSOLETE.mm
groff -mm -Tascii OBSOLETE.mm > OBSOLETE
groff -mm -Tascii sh.memo > memo.txt
groff -mm -Tascii PROMO.mm > PROMO

%post
umask 022
/sbin/ldconfig
if [ ! -f /etc/shells ]; then
	echo "/bin/ksh93" > /etc/shells
else
	while read SHNAME; do
		if [ "$SHNAME" = "/bin/ksh93" ]; then
			HAS_KSH=1
		fi
%if %{with binsh}
		if [ "$SHNAME" = "/bin/sh" ]; then
			HAS_SH=1
		fi
%endif
	done < /etc/shells
	[ -n "$HAS_KSH" ] || echo "/bin/ksh93" >> /etc/shells
%if %{with binsh}
	[ -n "$HAS_SH" ] || echo "/bin/sh" >> /etc/shells
%endif
fi

%preun
umask 022
if [ "$1" = "0" ]; then
	while read SHNAME; do
		[ "$SHNAME" = "/bin/ksh93" ] ||\
%if %{with binsh}
		[ "$SHNAME" = "/bin/sh" ] ||\
%endif
		echo "$SHNAME"
	done < /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi

%postun	-p /sbin/ldconfig

%post static
umask 022
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

%preun static
umask 022
if [ "$1" = "0" ]; then
	while read SHNAME; do
		[ "$SHNAME" = "/bin/ksh93.static" ] ||\
		echo "$SHNAME"
	done < /etc/shells > /etc/shells.new
	mv -f /etc/shells.new /etc/shells
fi

%files
%defattr(644,root,root,755)
%doc LICENSE
%doc src/cmd/ksh93/{COMPATIBILITY,RE*,builtins.mm,OBSOLETE,memo.txt,PROMO}

%attr(755,root,root) /bin/ksh93
%attr(755,root,root) /lib/libksh.so.*

%{_mandir}/man1/*

%if %{with binsh}
%attr(755,root,root) /bin/sh
%endif

%if %{with static}
%files static
%defattr(644,root,root,755)
%attr(755,root,root) /bin/ksh93.static
%endif

%clean
rm -rf $RPM_BUILD_ROOT
