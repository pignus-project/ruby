%define manver		1.4.6
Summary: An interpreter of object-oriented scripting language
Name: ruby
Version: 1.6.4
Release: 2
License: Dual-licensed GPL/Artistic-like
Group: Development/Languages
Source0: ftp://ftp.ruby-lang.org/pub/lang/%{name}/%{name}-%{version}.tar.bz2
Source1: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/%{name}-man-%{manver}.tar.bz2
Source2: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/%{name}-man-%{manver}-jp.tar.bz2
Source3: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/rubyfaq-990927.tar.bz2
Source4: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/rubyfaq-jp-990927.tar.bz2
Source5: irb.1
URL: http://www.ruby-lang.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel tcl tk autoconf gcc
Requires: %{name}-libs = %{version}-%{release}
ExcludeArch: alpha ia64

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.

%package libs
Summary: Libraries necessary to run Ruby.
Group: Development/Libraries
URL: http://www.ruby-lang.org/
Provides: libruby
Obsoletes: libruby

%description libs
This package includes the libruby, necessary to run Ruby.

%package devel
Summary: A Ruby development environment.
Group: Development/Languages
Requires: %{name} = %{version}-%{release}
URL: http://www.ruby-lang.org/

%description devel
Header files and libraries for building a extension library for the
Ruby or an application embedded Ruby.

%package tcltk
Summary: Tcl/Tk interface for scripting language Ruby.
Group: Development/Languages
Requires: %{name}-libs = %{version}-%{release}
URL: http://www.ruby-lang.org/

%description tcltk
Tcl/Tk interface for the object-oriented scripting language Ruby.

%package -n irb
Summary: The Intaractive Ruby.
Group: Development/Languages
Requires: %{name}-libs = %{version}-%{release}
URL: http://www.ruby-lang.org/

%description -n irb
The irb is acronym for Interactive RuBy.  It evaluates ruby expression
from the terminal.

%package docs
Summary: Manuals and FAQs for scripting language Ruby.
Group: Documentation
URL: http://www.ruby-lang.org/

%description docs
Manuals and FAQs for the object-oriented scripting language Ruby.

%prep
%setup -q -c -a 1 -a 2 -a 3 -a 4

%build
cd %{name}-%{version}
%ifarch alpha
autoconf
CFLAGS="-O0" CXXFLAGS="-O0" ./configure \
%else
%configure \
%endif
  --with-default-kcode=none \
  --with-dbm-include=/usr/include/db1 \
  --enable-shared \
  --enable-ipv6 \
  --with-lookup-order-hack=INET

make
make test

%install
rm -rf ${RPM_BUILD_ROOT}

# installing documents and exapmles...
mkdir tmp-ruby-docs
cd tmp-ruby-docs

# for ruby.rpm
mkdir ruby
cd ruby
(cd ../../%{name}-%{version} && 
 tar cf - misc sample lib/README*) | tar xvf -
(cd ../../%{name}-%{version} && 
 tar cf - `find ext \
  -mindepth 1 \
  \( -path '*/sample/*' -o -path '*/demo/*' \) -o \
  \( -name '*.rb' -not -path '*/lib/*' -not -name extconf.rb \) -o \
  \( -name 'README*' -o -name '*.txt*' -o -name 'MANUAL*' \)`) | tar xvf -

# fixing `#!' paths
for f in `find . -type f`
do
  sed -e 's,^#![ 	]*\([^ 	]*\)/\(ruby\|with\|perl\|env\),#!/usr/bin/\2,' < $f > $f.n
  mv -f $f.n $f
done

cd ..
# for ruby-devel.rpm
mkdir ruby-devel
cd ruby-devel

cd ..
# for ruby-tcltk.rpm
mkdir ruby-tcltk
cd ruby-tcltk
for target in tcltklib tk
do
 (cd ../ruby && 
  tar cf - `find . -path "*/$target/*"`) | tar xvf -
 (cd ../ruby && 
  rm -rf `find . -name "$target" -type d`)
done

cd ..
# for ruby-docs.rpm
mkdir ruby-docs
cd ruby-docs
mkdir doc-en doc-ja faq-en faq-ja
(cd ../../ruby-man-`echo %{manver} | sed -e 's/\.[0-9]*$//'` && tar cf - .) | (cd doc-en && tar xvf -)
(cd ../../ruby-man-`echo %{manver} | sed -e 's/\.[0-9]*$//'`-jp && tar cf - .) | (cd doc-ja && tar xvf -)
(cd ../../rubyfaq && tar cf - .) | (cd faq-en && tar xvf -)
(cd ../../rubyfaq-jp && tar cf - .) | (cd faq-ja && tar xvf -)

(cd faq-ja &&
 for f in rubyfaq-jp*.html
 do
  sed -e 's/\(<a href="rubyfaq\)-jp\(\|-[0-9]*\)\(.html\)/\1\2\3/g' \
   < $f > `echo $f | sed -e's/-jp//'`
  rm -f $f; \
 done)


# done
cd ../..

# installing binaries ...
cd %{name}-%{version}
make DESTDIR=${RPM_BUILD_ROOT} install
cd ..

# XXX: installing irb
#mv tmp-ruby-docs/ruby/sample/irb.rb $RPM_BUILD_ROOT%{_bindir}/irb
chmod 555 $RPM_BUILD_ROOT%{_bindir}/irb
install ${RPM_SOURCE_DIR}/irb.1 $RPM_BUILD_ROOT%{_mandir}/man1/

# listing all files in ruby-all.files
(find $RPM_BUILD_ROOT%{_bindir} \
      $RPM_BUILD_ROOT%{_libdir} \
      $RPM_BUILD_ROOT%{_mandir} \
      -type f -o -type l) | 
 sort | sed -e "s,^$RPM_BUILD_ROOT,," \
            -e "s,\(/man/man./.*\)$,\1*," > ruby-all.files
egrep '(\.[ah]|libruby\.so)$' ruby-all.files > ruby-devel.files

# for ruby-tcltk.rpm
cp /dev/null ruby-tcltk.files
for f in `cd %{name}-%{version}/ext/tk && find lib -type f; echo *.so`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files
done
for f in `cd %{name}-%{version}/ext/tcltklib && find lib -type f; echo *.so`
do
  grep "/`basename $f`$" ruby-all.files >> ruby-tcltk.files
done

# for irb.rpm
fgrep 'irb' ruby-all.files > irb.files

# for ruby-libs
cp /dev/null ruby-libs.files
(fgrep    '%{_libdir}' ruby-all.files; 
 fgrep -h '%{_libdir}' ruby-devel.files ruby-tcltk.files irb.files) | 
 sort | uniq -u > ruby-libs.files

# for ruby.rpm
sort ruby-all.files \
 ruby-libs.files ruby-devel.files ruby-tcltk.files irb.files | 
 uniq -u > ruby.files

strip ${RPM_BUILD_ROOT}%{_bindir}/%{name}

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -f *.files
rm -rf tmp-ruby-docs

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%files -f ruby.files
%defattr(-, root, root)
%doc %{name}-%{version}/README
%lang(ja) %doc %{name}-%{version}/README.jp
%doc %{name}-%{version}/COPYING*
%doc %{name}-%{version}/ChangeLog
%doc %{name}-%{version}/ToDo 
%doc %{name}-%{version}/doc/NEWS 
%doc tmp-ruby-docs/ruby/*

%files devel -f ruby-devel.files
%defattr(-, root, root)
%doc %{name}-%{version}/README.EXT
%lang(ja) %doc %{name}-%{version}/README.EXT.jp

%files libs -f ruby-libs.files
%defattr(-, root, root)
%doc %{name}-%{version}/README
%lang(ja) %doc %{name}-%{version}/README.jp
%doc %{name}-%{version}/doc/NEWS 

%files tcltk -f ruby-tcltk.files
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-tcltk/ext/*

%files -n irb -f irb.files
%defattr(-, root, root)

%files docs
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-docs/*

%changelog
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
