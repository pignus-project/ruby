%define manver		1.4.6
%define	rubyxver	1.8
%define	sitedir		%{_libdir}/site_ruby

Name:		ruby
Version:	1.8.2
Release: 1
License:	Distributable
URL:		http://www.ruby-lang.org/
BuildRoot:	%{_tmppath}/%{name}-%{version}-root
BuildRequires:	readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel tcl tk XFree86-devel autoconf gcc unzip openssl-devel db4-devel
BuildPreReq:	emacs

Source0:	ftp://ftp.ruby-lang.org/pub/%{name}/%{name}-%{version}.tar.gz
##Source1:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/%{name}-man-%{manver}.tar.gz
Source1:	%{name}-man-%{manver}.tar.bz2
Source2:	http://www7.tok2.com/home/misc/files/%{name}/%{name}-refm-rdp-1.8.1-ja-html.tar.gz
##Source3:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/rubyfaq-990927.tar.gz
Source3:	rubyfaq-990927.tar.bz2
##Source4:	ftp://ftp.ruby-lang.org/pub/%{name}/doc/rubyfaq-jp-990927.tar.gz
Source4:	rubyfaq-jp-990927.tar.bz2
Source5:	irb.1
Source10:	ruby-mode-init.el

Patch1:		ruby-1.8.0-multilib.patch

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
Summary:	The Interactive Ruby.
Group:		Development/Languages
Requires:	%{name} = %{version}-%{release}

%description -n irb
The irb is acronym for Interactive Ruby.  It evaluates ruby expression
from the terminal.


%package docs
Summary:	Manuals and FAQs for scripting language Ruby.
Group:		Documentation

%description docs
Manuals and FAQs for the object-oriented scripting language Ruby.


%package mode
Summary:	Emacs Lisp ruby-mode for the scripting language Ruby
Group:		Applications/Editors
Requires:	emacs-common

%description mode
Emacs Lisp ruby-mode for the object-oriented scripting language Ruby.


%package -n ri
Summary:	Ruby interactive reference
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description -n ri
ri is a command line tool that displays descriptions of built-in
Ruby methods, classes and modules. For methods, it shows you the calling
sequence and a description. For classes and modules, it shows a synopsis
along with a list of the methods the class or module implements.


%prep
%setup -q -c -a 1 -a 3 -a 4
mkdir -p ruby-refm-ja
pushd ruby-refm-ja
tar fxz %{SOURCE2}
popd
pushd %{name}-%{version}
%patch1 -p1
popd

%build
pushd %{name}-%{version}
for i in config.sub config.guess; do
	test -f %{_datadir}/libtool/$i && cp %{_datadir}/libtool/$i .
done
autoconf

rb_cv_func_strtod=no
export rb_cv_func_strtod
%if ia64
export RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed 's/-O[1-9]/-O0/g'`
%endif
CFLAGS="$RPM_OPT_FLAGS -Wall"
export CFLAGS
%configure \
  --with-sitedir='%{sitedir}' \
  --with-default-kcode=none \
  --enable-shared \
  --enable-ipv6 \
  --with-lookup-order-hack=INET \
  --disable-rpath

make RUBY_INSTALL_NAME=ruby %{?_smp_mflags}
%ifarch ia64
# Miscompilation? Buggy code?
rm -f parse.o
make OPT=-O0 RUBY_INSTALL_NAME=ruby %{?_smp_mflags}
%endif
%ifnarch ppc64
make test
%endif

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

# generate ri doc
DESTDIR=$RPM_BUILD_ROOT LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir} $RPM_BUILD_ROOT%{_bindir}/ruby -I $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version} -I $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}/ext/syck -I $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}/lib $RPM_BUILD_ROOT%{_bindir}/rdoc --all --ri-system $RPM_BUILD_DIR/%{name}-%{version}/%{name}-%{version}

# XXX: installing irb
chmod 555 $RPM_BUILD_ROOT%{_bindir}/irb
install %{SOURCE5} $RPM_BUILD_ROOT%{_mandir}/man1/

# installing ruby-mode
cd %{name}-%{version}
cp misc/*.el $RPM_BUILD_ROOT%{_datadir}/emacs/site-lisp/ruby-mode

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
for f in `find %{name}-%{version}/ext/tk/lib -type f; find %{name}-%{version}/ext/tk -type f -name '*.so'`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files || :
done
for f in `find %{name}-%{version}/ext/tcltklib/lib -type f; find %{name}-%{version}/ext/tcltklib -type f -name '*.so'`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files || :
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
fgrep '.el' ruby-all.files >> ruby-mode.files

# for ri
cp /dev/null ri.files
fgrep '%{_datadir}/ri' ruby-all.files >> ri.files
fgrep '%{_bindir}/ri' ruby-all.files >> ri.files

# for ruby.rpm
sort ruby-all.files \
 ruby-libs.files ruby-devel.files ruby-tcltk.files irb.files ruby-mode.files ri.files | 
 uniq -u > ruby.files

# for arch-dependent dir
rbconfig=`find $RPM_BUILD_ROOT -name rbconfig.rb`
export LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir}
arch=`$RPM_BUILD_ROOT%{_bindir}/ruby -r $rbconfig -e 'printf ("%s\n", Config::CONFIG["arch"])'`
cat <<__EOF__ >> ruby-libs.files
%%dir %%{_libdir}/ruby/%%{rubyxver}/$arch
%%dir %%{_libdir}/ruby/%%{rubyxver}/$arch/digest
%%dir %%{sitedir}/%%{rubyxver}/$arch
__EOF__

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT
rm -f *.files
rm -rf tmp-ruby-docs

%post libs
/sbin/ldconfig

%postun libs
/sbin/ldconfig

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
%dir %{_libdir}/ruby
%dir %{_libdir}/ruby/%{rubyxver}
%dir %{_libdir}/ruby/%{rubyxver}/cgi
%dir %{_libdir}/ruby/%{rubyxver}/net
%dir %{_libdir}/ruby/%{rubyxver}/shell
%dir %{_libdir}/ruby/%{rubyxver}/uri
%dir %{sitedir}
%dir %{sitedir}/%{rubyxver}

%files tcltk -f ruby-tcltk.files
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-tcltk/ext/*

%files -n irb -f irb.files
%defattr(-, root, root)
%doc tmp-ruby-docs/irb/*
%dir %{_libdir}/ruby/%{rubyxver}/irb
%dir %{_libdir}/ruby/%{rubyxver}/irb/lc
%dir %{_libdir}/ruby/%{rubyxver}/irb/lc/ja

%files -n ri -f ri.files
%defattr(-, root, root)
%dir %{_datadir}/ri

%files docs
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-docs/*

%files mode -f ruby-mode.files 
%defattr(-, root, root)
%doc %{name}-%{version}/misc/README
%dir %{_datadir}/emacs/site-lisp/ruby-mode

%changelog
* Wed Jan  5 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-1
- New upstream release.
- ruby-1.8.1-ia64-stack-limit.patch: removed - it's no longer needed.
- ruby-1.8.1-cgi_session_perms.patch: likewise.
- ruby-1.8.1-cgi-dos.patch: likewise.
- generated Ruby interactive documentation - senarated package.
  it's now provided as ri package. (#141806)

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 1.8.1-10
- rebuild against db-4.3.21.

* Wed Nov 10 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-9
- ruby-1.8.1-cgi-dos.patch: security fix [CAN-2004-0983]
- ruby-1.8.1-cgi_session_perms.patch: security fix [CAN-2004-0755]

* Fri Oct 29 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-8
- added openssl-devel and db4-devel into BuildRequires (#137479)

* Wed Oct  6 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-7
- require emacs-common instead of emacs.

* Wed Jun 23 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-4
- updated the documentation.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 04 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-1
- New upstream release.
- don't use any optimization for ia64 to avoid the build failure.
- ruby-1.8.1-ia64-stack-limit.patch: applied to fix SystemStackError when the optimization is disabled.

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-3
- rebuild against db-4.2.52.

* Thu Sep 25 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-2
- rebuild against db-4.2.42.

* Tue Aug  5 2003 Akira TAGOH <tagoh@redhat.com> 1.8.0-1
- New upstream release.

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9.1
- rebuilt

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9
- ruby-1.6.8-castnode.patch: handling the nodes with correct cast.
  use this patch now instead of ruby-1.6.8-fix-x86_64.patch.

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-8
- rebuilt

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-7
- fix the gcc warnings. (#82192)
- ruby-1.6.8-fix-x86_64.patch: correct a patch.
  NOTE: DON'T USE THIS PATCH FOR BIG ENDIAN ARCHITECTURE.
- ruby-1.6.7-long2int.patch: removed.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb  7 2003 Jens Petersen <petersen@redhat.com> - 1.6.8-5
- rebuild against ucs4 tcltk

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 22 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-3
- ruby-1.6.8-multilib.patch: applied to fix the search path issue on x86_64

* Tue Jan 21 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-2
- ruby-1.6.8-require.patch: applied to fix the search bug in require.
- don't apply long2int patch to s390 and s390x. it doesn't work.

* Wed Jan 15 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-1
- New upstream release.
- removed some patches. it's no longer needed.
  - ruby-1.6.7-100.patch
  - ruby-1.6.7-101.patch
  - ruby-1.6.7-102.patch
  - ruby-1.6.7-103.patch
  - 801_extmk.rb-shellwords.patch
  - 801_mkmf.rb-shellwords.patch
  - 804_parse.y-new-bison.patch
  - 805_uri-bugfix.patch
  - ruby-1.6.6-900_XXX_strtod.patch
  - ruby-1.6.7-sux0rs.patch
  - ruby-1.6.7-libobj.patch

* Wed Jan 15 2003 Jens Petersen <petersen@redhat.com> 1.6.7-14
- rebuild to update tcltk deps

* Mon Dec 16 2002 Elliot Lee <sopwith@redhat.com> 1.6.7-13
- Remove ExcludeArch: x86_64
- Fix x86_64 ruby with long2int.patch (ruby was assuming that sizeof(long) 
  == sizeof(int). The patch does not fix the source of the problem, just 
  makes it a non-issue.)
- _smp_mflags

* Tue Dec 10 2002 Tim Powers <timp@redhat.com> 1.6.7-12
- rebuild to fix broken tcltk deps

* Tue Oct 22 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-11
- use %%configure macro instead of configure script.
- use the latest config.{sub,guess}.
- get archname from rbconfig.rb for %%dir
- applied some patches from Debian:
  - 801_extmk.rb-shellwords.patch: use Shellwords
  - 801_mkmf.rb-shellwords.patch: mkmf.rb creates bad Makefile. the Makefile
    links libruby.a to the target.
  - 803_sample-fix-shbang.patch: all sample codes should be
    s|/usr/local/bin|/usr/bin|g
  - 804_parse.y-new-bison.patch: fix syntax warning.
  - 805_uri-bugfix.patch: uri.rb could not handle correctly broken mailto-uri.
- add ExcludeArch x86_64 temporarily to fix Bug#74581. Right now ruby can't be
  built on x86_64.

* Tue Aug 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-10
- moved sitedir to /usr/lib/ruby/site_ruby again according as our perl and
  python.
- ruby-1.6.7-resolv1.patch, ruby-1.6.7-resolv2.patch: applied to fix 'Too many
  open files - "/etc/resolv.conf"' issue. (Bug#64830)

* Thu Jul 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-9
- add the owned directory.

* Fri Jul 12 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-8
- fix typo.

* Thu Jul 04 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-7
- removed the ruby-mode-xemacs because it's merged to the xemacs sumo.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jun 19 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-5
- fix the stripped binary.
- use the appropriate macros.

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-3
- ruby-1.6.7-libobj.patch: applied to fix autoconf2.53 error.

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
