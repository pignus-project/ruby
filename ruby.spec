%define manver		1.4.6
%define	rubyxver	1.6
%define	sitedir		%{_prefix}/local/lib/site_ruby/%{rubyxver}

Name:		ruby
Version:	1.6.7
Release:	2
License:	Distributable
URL:		http://www.ruby-lang.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel tcl tk XFree86-devel autoconf gcc
BuildPreReq:	emacs xemacs


## all archives are re-compressed with bzip2 instead of gzip
##Source0:	ftp://ftp.ruby-lang.org/pub/%{name}/%{name}-%{version}.tar.gz
Source0:	%{name}-%{version}.tar.bz2
##Source1:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/%{name}-man-%{manver}.tar.gz
Source1:	%{name}-man-%{manver}.tar.bz2
##Source2:	http://www7.tok2.com/home/misc/files/%{name}/%{name}-refm-rdp-1.4.7-ja-html.zip
Source2:	%{name}-man-%{version}-ja-html.tar.bz2
##Source3:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/rubyfaq-990927.tar.gz
Source3:	rubyfaq-990927.tar.bz2
##Source4:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/rubyfaq-jp-990927.tar.gz
Source4:	rubyfaq-jp-990927.tar.bz2
Source5:	irb.1
Source10:	ruby-mode-init.el

Patch100:	ruby-1.6.7-100.patch
Patch101:	ruby-1.6.7-101.patch
Patch102:	ruby-1.6.7-102.patch
Patch103:	ruby-1.6.7-103.patch
Patch900:	ruby-1.6.6-900-XXX-strtod.patch


Summary:	An interpreter of object-oriented scripting language
Group:		Development/Languages
Requires:	%{name}-libs = %{version}-%{release}

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.


%package libs
Summary:	Libraries necessary to run Ruby.
Group:		Development/Libraries
Provides:	libruby
Obsoletes:	libruby

%description libs
This package includes the libruby, necessary to run Ruby.


%package devel
Summary:	A Ruby development environment.
Group:		Development/Languages
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files and libraries for building a extension library for the
Ruby or an application embedded Ruby.


%package tcltk
Summary:	Tcl/Tk interface for scripting language Ruby.
Group:		Development/Languages
Requires:	%{name}-libs = %{version}-%{release}

%description tcltk
Tcl/Tk interface for the object-oriented scripting language Ruby.


%package -n irb
Summary:	The Intaractive Ruby.
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description -n irb
The irb is acronym for Interactive RuBy.  It evaluates ruby expression
from the terminal.


%package docs
Summary:	Manuals and FAQs for scripting language Ruby.
Group:		Documentation

%description docs
Manuals and FAQs for the object-oriented scripting language Ruby.


%package mode
Summary:	Emacs Lisp ruby-mode for the scripting language Ruby
Group:		Applications/Editors
Requires:	emacs

%description mode
Emacs Lisp ruby-mode for the object-oriented scripting language Ruby.


%package mode-xemacs
Summary:	Emacs Lisp ruby-mode for the scripting language Ruby
Group:		Applications/Editors
Requires:	xemacs
ExcludeArch:	alpha

%description mode-xemacs
Emacs Lisp ruby-mode for the object-oriented scripting language Ruby.


%prep
%setup -q -c -a 1 -a 2 -a 3 -a 4
pushd %{name}-%{version}
%patch100 -p1
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch900 -p1
popd

%build
pushd %{name}-%{version}
autoconf

%ifarch alpha ia64
rb_cv_func_strtod=no CFLAGS="-O0" CXXFLAGS="-O0" ./configure \
%else
rb_cv_func_strtod=no ./configure \
%endif
  --prefix=%{_prefix} \
  --mandir='${prefix}/share/man' \
  --sysconfdir=%{_sysconfdir} \
  --localstatedir=%{_localstatedir} \
  --with-sitedir='${prefix}/local/lib/site_ruby/%{rubyxver}' \
  --with-default-kcode=none \
  --with-dbm-include=/usr/include/db1 \
  --enable-shared \
  --enable-ipv6 \
  --with-lookup-order-hack=INET \
  %{_target_cpu}-%{_target_os}

make
make test

popd

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/ruby-mode
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/site-start.d
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/xemacs/xemacs-packages/lisp/ruby-mode
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/xemacs/xemacs-packages/lisp/site-start.d

# installing documents and exapmles...
mkdir tmp-ruby-docs
cd tmp-ruby-docs

# for ruby.rpm
mkdir ruby ruby-libs ruby-devel ruby-tcltk ruby-docs irb
cd ruby
(cd ../../%{name}-%{version} && tar cf - sample) | tar xvf -
cd ..

# for ruby-libs
cd ruby-libs
(cd ../../%{name}-%{version} && tar cf - lib/README*) | tar xvf -
(cd ../../%{name}-%{version}/doc && tar cf - .) | tar xvf -
(cd ../../%{name}-%{version} &&
 tar cf - `find ext \
  -mindepth 1 \
  \( -path '*/sample/*' -o -path '*/demo/*' \) -o \
  \( -name '*.rb' -not -path '*/lib/*' -not -name extconf.rb \) -o \
  \( -name 'README*' -o -name '*.txt*' -o -name 'MANUAL*' \)`) | tar xvf -
cd ..

# for irb
cd irb
mv ../ruby-libs/irb/* .
rmdir ../ruby-libs/irb
cd ..

# for ruby-devel
cd ruby-devel

cd ..

# for ruby-tcltk
cd ruby-tcltk
for target in tcltklib tk
do
 (cd ../ruby-libs &&
  tar cf - `find . -path "*/$target/*"`) | tar xvf -
 (cd ../ruby-libs &&
  rm -rf `find . -name "$target" -type d`)
done
cd ..

# for ruby-docs
cd ruby-docs
mkdir doc-en refm-ja faq-en faq-ja
(cd ../../ruby-man-`echo %{manver} | sed -e 's/\.[0-9]*$//'` && tar cf - .) | (cd doc-en && tar xvf -)
(cd ../../ruby-refm-ja && tar cf - .) | (cd refm-ja && tar xvf -)
(cd ../../rubyfaq && tar cf - .) | (cd faq-en && tar xvf -)
(cd ../../rubyfaq-jp && tar cf - .) | (cd faq-ja && tar xvf -)

(cd faq-ja &&
 for f in rubyfaq-jp*.html
 do
  sed -e 's/\(<a href="rubyfaq\)-jp\(\|-[0-9]*\)\(.html\)/\1\2\3/g' \
   < $f > `echo $f | sed -e's/-jp//'`
  rm -f $f; \
 done)

cd ..

# fixing `#!' paths
for f in `find . -type f`
do
  sed -e 's,^#![ 	]*\([^ 	]*\)/\(ruby\|with\|perl\|env\),#!/usr/bin/\2,' < $f > $f.n
  if ! cmp $f $f.n
  then
    mv -f $f.n $f
  else
    rm -f $f.n
  fi
done

# done
cd ..

# installing binaries ...
cd %{name}-%{version}
make DESTDIR=$RPM_BUILD_ROOT install
cd ..

# XXX: installing irb
chmod 555 $RPM_BUILD_ROOT%{_bindir}/irb
install %{SOURCE5} $RPM_BUILD_ROOT%{_mandir}/man1/

# installing ruby-mode
cd %{name}-%{version}
cp misc/*.el $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/ruby-mode
cp misc/*.el $RPM_BUILD_ROOT%{_libdir}/xemacs/xemacs-packages/lisp/ruby-mode

## for ruby-mode
pushd $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/ruby-mode
cat <<EOF > path.el
(setq load-path (cons "." load-path) byte-compile-warnings nil)
EOF
emacs --no-site-file -q -batch -l path.el -f batch-byte-compile *.el
rm -f path.el*
popd
install -m 644 %{SOURCE10} \
	$RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/site-start.d

## for ruby-mode-xemacs
pushd $RPM_BUILD_ROOT%{_libdir}/xemacs/xemacs-packages/lisp/ruby-mode
cat <<EOF > path.el
(setq load-path (cons "." load-path) byte-compile-warnings nil)
EOF
xemacs -no-site-file -q -batch -l path.el -f batch-byte-compile *.el
rm -f path.el*
popd
install -m 644 %{SOURCE10} \
	$RPM_BUILD_ROOT%{_libdir}/xemacs/xemacs-packages/lisp/site-start.d

cd ..

# listing all files in ruby-all.files
(find $RPM_BUILD_ROOT%{_bindir} \
      $RPM_BUILD_ROOT%{_datadir} \
      $RPM_BUILD_ROOT%{_libdir} \
      $RPM_BUILD_ROOT%{_mandir} \
      -type f -o -type l) | 
 sort | uniq | sed -e "s,^$RPM_BUILD_ROOT,," \
                   -e "s,\(/man/man./.*\)$,\1*," > ruby-all.files
egrep '(\.[ah]|libruby\.so)$' ruby-all.files > ruby-devel.files

# for ruby-tcltk.rpm
cp /dev/null ruby-tcltk.files
for f in `find %{name}-%{version}/ext/tk/lib -type f; echo %{name}-%{version}/ext/tk/*.so`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files
done
for f in `find %{name}-%{version}/ext/tcltklib/lib -type f; echo %{name}-%{version}/ext/tcltklib/*.so`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files
done

# for irb.rpm
fgrep 'irb' ruby-all.files > irb.files

# for ruby-libs
cp /dev/null ruby-libs.files
(fgrep    '%{_libdir}' ruby-all.files; 
 fgrep -h '%{_libdir}' ruby-devel.files ruby-tcltk.files irb.files) | egrep -v "elc?$" | \
 sort | uniq -u > ruby-libs.files

# for ruby-mode
cp /dev/null ruby-mode.files
fgrep '.el' ruby-all.files | grep -v xemacs >> ruby-mode.files

# for ruby-mode-xemacs
cp /dev/null ruby-mode-xemacs.files
fgrep '.el' ruby-all.files | grep -v share >> ruby-mode-xemacs.files

# for ruby.rpm
sort ruby-all.files \
 ruby-libs.files ruby-devel.files ruby-tcltk.files irb.files ruby-mode.files ruby-mode-xemacs.files | 
 uniq -u > ruby.files

strip $RPM_BUILD_ROOT%{_bindir}/%{name}

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT
rm -f *.files
rm -rf tmp-ruby-docs

%post libs
/sbin/ldconfig
if [ -w %{_prefix}/local/lib -a ! -e %{sitedir} ]; then
	mkdir -p %{sitedir} %{sitedir}/%{_target_cpu}-%{_target_os}
	chown root.root %{sitedir} %{sitedir}/%{_target_cpu}-%{_target_os}
	chmod 2775 %{sitedir} %{sitedir}/%{_target_cpu}-%{_target_os}
fi

%postun libs
/sbin/ldconfig
if [ "$1" = 0 ]; then
	if [ -w %{sitedir} -a -e %{sitedir}/%{_target_cpu}-%{_target_os} ]; then
		rmdir %{sitedir}/%{_target_cpu}-%{_target_os} 2>/dev/null || true
	fi
	if [ -w %{_prefix}/local/lib -a -e %{sitedir} ]; then
		rmdir %{sitedir} 2>/dev/null || true
	fi
fi

%files -f ruby.files
%defattr(-, root, root)
%doc %{name}-%{version}/README
%lang(ja) %doc %{name}-%{version}/README.ja
%doc %{name}-%{version}/COPYING*
%doc %{name}-%{version}/ChangeLog
%doc %{name}-%{version}/LEGAL
%doc %{name}-%{version}/ToDo 
%doc %{name}-%{version}/doc/NEWS 
%doc tmp-ruby-docs/ruby/*

%files devel -f ruby-devel.files
%defattr(-, root, root)
%doc %{name}-%{version}/README.EXT
%lang(ja) %doc %{name}-%{version}/README.EXT.ja

%files libs -f ruby-libs.files
%defattr(-, root, root)
%doc %{name}-%{version}/README
%lang(ja) %doc %{name}-%{version}/README.ja
%doc %{name}-%{version}/COPYING*
%doc %{name}-%{version}/ChangeLog
%doc %{name}-%{version}/LEGAL
%doc tmp-ruby-docs/ruby-libs/*

%files tcltk -f ruby-tcltk.files
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-tcltk/ext/*

%files -n irb -f irb.files
%defattr(-, root, root)
%doc tmp-ruby-docs/irb/*

%files docs
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-docs/*

%files mode -f ruby-mode.files 
%defattr(-, root, root)
%doc %{name}-%{version}/misc/README

%files mode-xemacs -f ruby-mode-xemacs.files
%defattr(-, root, root)
%doc %{name}-%{version}/misc/README

%changelog
* Mon Mar 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-2
- ruby-man-1.4.6-jp.tar.bz2: removed.
- ruby-refm-rdp-1.4.7-ja-html.tar.bz2: uses it instead of.
- ruby-1.6.7-500-marshal-proc.patch, ruby-1.6.7-501-class-var.patch:
  removed.
- ruby-1.6.7-100.patch: applied a bug fix patch.
  (ruby-dev#16274: patch for 'wm state')
  (PR#206ja: SEGV handle EXIT) 
- ruby-1.6.7-101.patch: applied a bug fix patch.
  (ruby-list#34313: singleton should not be Marshal.dump'ed)
  (ruby-dev#16411: block local var)
- ruby-1.6.7-102.patch: applied a bug fix patch.
  (handling multibyte chars is partially broken)
- ruby-1.6.7-103.patch: applied a bug fix patch.
  (ruby-dev#16462: preserve reference for GC, but link should be cut)

* Fri Mar  8 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-1
- New upstream release.
- ruby-1.6.6-100.patch, ruby-1.6.6-501-ruby-mode.patch:
  removed. these patches no longer should be needed.
- ruby-1.6.7-500-marshal-proc.patch: applied a fix patch.
  (ruby-dev#16178: Marshal::dump should call Proc#call.)
- ruby-1.6.7-501-class-var.patch: applied a fix patch.
  (ruby-talk#35157: class vars broken in 1.6.7)

* Wed Feb 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-5
- Disable alpha because nothing is xemacs for alpha now.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-3
- Fixed the duplicate files.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-2
- Fixed the missing %%defattr

* Fri Feb  1 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-1
- New upstream release.
- Applied bug fix patches:
  - ruby-1.6.6-501-ruby-mode.patch: ruby-talk#30479: disables font-lock
    coloring.
  - ruby-1.6.6-100.patch: ruby-talk#30203: Ruby 1.6.6 bug and fix
                          ruby-list#33047: regex bug
                          PR#230: problem with -d in 1.6.6
- Added ruby-mode and ruby-mode-xemacs packages.
- Ruby works fine for ia64. so re-enable to build with ia64.
  (probably it should be worked for alpha)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jul 19 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.4-2
- Remove Japanese description and summaries; they belong in specspo and
  break rpm
- Clean up specfile
- Mark language specific files (README.jp) as such
- bzip2 sources
- rename the libruby package to ruby-libs for consistency
- Exclude ia64 (doesn't build - the code doesn't seem to be 64-bit clean
  [has been excluded on alpha forever])

* Tue Jul 17 2001 Akira TAGOH <tagoh@redhat.com> 1.6.4-1
- rebuild for Red Hat 7.2

* Mon Jun 04 2001 akira yamada <akira@vinelinux.org>
- upgrade to nwe upstream version 1.6.4.

* Mon Apr 02 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed method cache bug. etc. (Patch103, Patch104)

* Tue Mar 27 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed marshal for bignum bug.
  - fixed scope of constant variables bug.

* Tue Mar 20 2001 akira yamada <akira@vinelinux.org>
- upgraded to new upstream version 1.6.3.

* Fri Feb 09 2001 akira yamada <akira@vinelinux.org>
- fixed bad group for libruby.
- Applied patch: upgraded to cvs version (2001-02-08):
  fixed minor bugs.

* Thu Jan 18 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-15):
  fixed minor bugs(e.g. ruby makes extention librares too large...).

* Wed Jan 10 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-09):
  fixed minor bugs.

* Sat Dec 30 2000 akira yamada <akira@vinelinux.org>
- Applied bug fix patch.

* Mon Dec 25 2000 akira yamada <akira@vinelinux.org>
- Updated to new upstream version 1.6.2.

* Fri Dec 22 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000122019.patch, added ruby_cvs.2000122215.patch
  (upgraded ruby to latest cvs version, 1.6.2-preview4).

* Wed Dec 20 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000121413.patch, added ruby_cvs.2000122019.patch
  (upgraded ruby to latest cvs version).
- new package: libruby

* Thu Dec 14 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000101901.patch, added ruby_cvs.2000121413.patch
  (upgraded ruby to latest cvs version).
- Removed ruby-dev.11262.patch, ruby-dev.11265.patch, 
  and ruby-dev.11268.patch (included into above patch).

* Sun Nov 12 2000 MACHINO, Satoshi <machino@vinelinux.org> 1.6.1-0vl9
- build on gcc-2.95.3

* Thu Oct 19 2000 akira yamada <akira@vinelinux.org>
- Added ruby-dev.11268.patch.

* Thu Oct 19 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000101117.patch and added ruby_cvs.2000101901.patch
  (upgraded ruby to latest cvs version).
- Added ruby-dev.11262.patch.
- Added ruby-dev.11265.patch.
  
* Wed Oct 11 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000101117.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 09 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Tue Oct 03 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100218.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 02 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000092718.patch and added ruby_cvs.2000100218.patch
  (upgraded ruby to latest cvs version).

* Thu Sep 27 2000 akira yamada <akira@vinelinux.org>
- Updated to upstream version 1.6.1.
- Removed ruby_cvs.2000082901.patch and added ruby_cvs.2000092718.patch
  (upgraded ruby to latest cvs version).

* Tue Aug 29 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.6.
- removed ruby-dev.10123.patch(included into ruby-1.4.6).
- Added ruby_cvs.2000082901.patch(upgraded ruby to latest cvs version).

* Tue Jun 27 2000 akira yamada <akira@redhat.com>
- Updated manuals to version 1.4.5.

* Sun Jun 25 2000 akira yamada <akira@redhat.com>
- Added ruby-dev.10123.patch.

* Sat Jun 24 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.5.
- Removed ruby_cvs.2000062401.patch(included into ruby-1.4.5).

* Thu Jun 22 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/22/2000 CVS).
- Removed ruby-dev.10054.patch(included into ruby_cvs.patch).

* Thu Jun 22 2000 akira yamada <akira@redhat.com>
- Renamed to ruby_cvs20000620.patch from ruby_cvs.patch.

* Tue Jun 20 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/20/2000 CVS).
- Removed ruby-list.23190.patch(included into ruby_cvs.patch).
- Added ruby-dev.10054.patch.

* Tue Jun 15 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/12/2000 CVS).
- Added manuals and FAQs.
- Split into ruby, ruby-devel, ruby-tcltk, ruby-docs, irb.

* Tue Jun 13 2000 Mitsuo Hamada <mhamada@redhat.com>
- Updated to version 1.4.4

* Wed Dec 08 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.3

* Mon Sep 20 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2 (Sep 18)

* Fri Sep 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2

* Tue Aug 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.0

* Fri Jul 23 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- 2nd release
- Updated to version 1.2.6(15 Jul 1999)
- striped %{prefix}/bin/ruby

* Mon Jun 28 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.6(21 Jun 1999)

* Wed Apr 14 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.5

* Fri Apr 09 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.4

* Fri Dec 25 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.2 stable.

* Fri Nov 27 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c9.

* Thu Nov 19 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c8, however it appear short life :-P

* Fri Nov 13 1998 Toru Hoshina <hoshina@best.com>
- Version up.

* Mon Sep 22 1998 Toru Hoshina <hoshina@best.com>
- To make a libruby.so.

* Mon Sep 21 1998 Toru Hoshina <hoshina@best.com>
- Modified SPEC in order to install libruby.a so that it should be used by
  another ruby entention.
- 2nd release.

* Mon Mar 9 1998 Shoichi OZAWA <shoch@jsdi.or.jp>
- Added a powerPC arch part. Thanks, MURATA Nobuhiro <nob@makioka.y-min.or.jp>
