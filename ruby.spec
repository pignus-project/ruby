%define	rubyver	1.4.6
%define manver	%{rubyver}
%define rpmrel	2
Summary: An interpeter of object-oriented scripting language
Name: ruby
Version: %{rubyver}
Release: %{rpmrel}
#Distribution: 
Copyright: distributable
Group: Development/Languages
Source0: ftp://ftp.netlab.co.jp/pub/lang/%{name}/%{name}-%{version}.tar.gz
Source1: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/%{name}-man-%{manver}.tar.gz
Source2: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/%{name}-man-%{manver}-jp.tar.gz
Source3: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/rubyfaq-990927.tar.gz
Source4: ftp://ftp.netlab.co.jp/pub/lang/%{name}/doc/rubyfaq-jp-990927.tar.gz
Patch1: ruby-jcode.rb-utf8.patch
Patch2: ruby_cvs.2000082917.patch
URL: http://www.ruby-lang.org/
Prefix: /usr
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildRequires: readline readline-devel ncurses ncurses-devel gdbm gdbm-devel glibc-devel tcl tk
Vendor: Red Hat, Inc.
Packager: akira yamada <akira@redhat.com>
Summary(ja): オブジェクト指向言語Rubyインタプリタ

%description
Ruby is the interpreted scripting language for quick and
easy object-oriented programming.  It has many features to
process text files and to do system management tasks (as in
Perl).  It is simple, straight-forward, and extensible.

%description -l ja
Rubyはシンプルかつ強力なオブジェクト指向スクリプト言語です．
Rubyは最初から純粋なオブジェクト指向言語として設計されていま
すから，オブジェクト指向プログラミングを手軽に行う事が出来ま
す．もちろん通常の手続き型のプログラミングも可能です．

Rubyはテキスト処理関係の能力などに優れ，Perlと同じくらい強力
です．さらにシンプルな文法と，例外処理やイテレータなどの機構
によって，より分かりやすいプログラミングが出来ます．

%package -n ruby-devel
Summary: A Ruby development environment.
Group: Development/Languages
Requires: ruby = %{PACKAGE_VERSION}
URL: http://www.ruby-lang.org/

%description -n ruby-devel
Header files and libraries for building a extension library for the
Ruby or an application embedded Ruby.

%description -n ruby-devel -l ja
Rubyのための拡張ライブラリやRubyを組み込んだアプリケーションを作るため
に必要となるへッダファイルやライブラリです．

%package -n ruby-tcltk
Summary: Tcl/Tk interface for scripting language Ruby.
Group: Development/Languages
Requires: ruby = %{PACKAGE_VERSION}
URL: http://www.ruby-lang.org/

%description -n ruby-tcltk
Tcl/Tk interface for the object-oriented scripting language Ruby.

%description -n ruby-tcltk -l ja
RubyにTcl/Tkライブラリへのインタフェースを提供する拡張ライブラリです．

%package -n irb
Summary: The Intaractive Ruby.
Group: Development/Languages
Requires: ruby = %{PACKAGE_VERSION}
URL: http://www.ruby-lang.org/

%description -n irb
The irb is acronym for Interactive RuBy.  It evaluates ruby expression
from the terminal.

%description -n irb -l ja
irbとはInteractive RuByの略で，対話的にRubyの式を入力し，評価させるこ
とが可能です．

%package -n ruby-docs
Summary: Manuals and FAQs for scripting language Ruby.
Group: Documentation
URL: http://www.ruby-lang.org/

%description -n ruby-docs
Manuals and FAQs for the object-oriented scripting language Ruby.

%description -n ruby-docs -l ja
オブジェクト指向スクリプト言語Rubyについてのマ二ュアルとFAQです．

%prep

%setup -q -c -a 1 -a 2 -a 3 -a 4

cd %{name}-%{version}
#%patch0 -p1
%patch1 -p1
%patch2 -p1

#%patch10 -p1

cd ../../..


%build

cd %{name}-%{version}
#CFLAGS="${RPM_OPT_FLAGS}" ./configure \
#  --prefix=%{prefix} \
#  --mandir=%{prefix}/man \
#  --with-default-kcode=none \
#  --with-dbm-include=/usr/include/db1 \
#  --enable-shared \
#  --enable-ipv6 \
#  --with-lookup-order-hack=INET
#  ${RPM_ARCH}-linux
%configure \
  --prefix=%{prefix} \
  --mandir=%{prefix}/share/man \
  --with-default-kcode=none \
  --with-dbm-include=/usr/include/db1 \
  --enable-shared \
  --enable-ipv6 \
  --with-lookup-order-hack=INET

make
make test

cd ..


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
 tar cf - `find ext 
  -mindepth 1 
  \( -path '*/sample/*' -o -path '*/demo/*' \) -o 
  \( -name '*.rb' -not -path '*/lib/*' -not -name extconf.rb \) -o 
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
mv tmp-ruby-docs/ruby/sample/irb.rb $RPM_BUILD_ROOT%{prefix}/bin/irb
chmod 555 $RPM_BUILD_ROOT%{prefix}/bin/irb

# listing all files in ruby-all.files
(find $RPM_BUILD_ROOT%{prefix}/bin \
      $RPM_BUILD_ROOT%{prefix}/lib \
      $RPM_BUILD_ROOT%{prefix}/man \
      -type f -o -type l) | 
 sort | sed -e "s,^$RPM_BUILD_ROOT,," > ruby-all.files
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
egrep 'irb' ruby-all.files > irb.files

# for ruby.rpm
sort ruby-all.files \
 ruby-devel.files ruby-tcltk.files irb.files | 
 uniq -u > ruby.files

strip ${RPM_BUILD_ROOT}%{prefix}/bin/%{name}

%clean
rm -rf ${RPM_BUILD_ROOT}
rm -f *.files
rm -rf tmp-ruby-docs

%post -p /sbin/ldconfig -n ruby

%postun -p /sbin/ldconfig -n ruby

%files -f ruby.files -n ruby
%defattr(-, root, root)
%doc %{name}-%{version}/README
%doc %{name}-%{version}/README.jp
%doc %{name}-%{version}/COPYING*
%doc %{name}-%{version}/ChangeLog
%doc %{name}-%{version}/ToDo 
%doc tmp-ruby-docs/ruby/*

%files -f ruby-devel.files -n ruby-devel
%defattr(-, root, root)
%doc %{name}-%{version}/README.EXT
%doc %{name}-%{version}/README.EXT.jp

%files -f ruby-tcltk.files -n ruby-tcltk
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-tcltk/ext/*

%files -f irb.files -n irb
%defattr(-, root, root)

%files -n ruby-docs
%defattr(-, root, root)
%doc tmp-ruby-docs/ruby-docs/*

%changelog
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
