# Maintainer: Tim Savannah <kata198@gmail.com>

pkgbase=python-queryablelist
pkgname=('python-queryablelist' 'python2-queryablelist')
pkgver=3.1.0
pkgrel=1
pkgdesc="Python module to add support for ORM-style filtering to any list of items"
arch=('any')
license=('LGPLv2')
url="http://github.com/kata198/QueryableList"
makedepends=('python-setuptools' 'python2-setuptools')
source=("https://pypi.python.org/packages/59/cd/ff38fb62fc81def97f50a98fc4bdbbe258351b5be8be6a6b69fec7a25c81/QueryableList-${pkgver}.tar.gz")
sha512sums=('4e4b69b3fcdc9c019fdb9fb7cc09b917f738a5b3d7b0f3bd4f19d2505a1caac04d1e5371e4ae25d278b960d0ee15af9b6c5c96c9e202c3bb2b8b2327aa320ccc')

prepare() {
  cp -a QueryableList-${pkgver}{,-python2}
}

build() {
  cd "$srcdir"/QueryableList-$pkgver
  python setup.py build

  cd "$srcdir"/QueryableList-$pkgver-python2
  python2 setup.py build
}

package_python-queryablelist() {
  cd QueryableList-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1 --skip-build
}

package_python2-queryablelist() {
  cd QueryableList-$pkgver-python2
  python2 setup.py install --root="$pkgdir" --optimize=1 --skip-build
}
