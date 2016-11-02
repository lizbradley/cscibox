# Documentation: https://github.com/Homebrew/brew/blob/master/share/doc/homebrew/Formula-Cookbook.md
#                http://www.rubydoc.info/github/Homebrew/brew/master/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!

class Cscibox < Formula
  desc "Geography Core Data Application"
  homepage "http://www.cs.colorado.edu/~lizb/cscience.html"
  url "https://github.com/ldevesine/cscibox/archive/0.11.2.tar.gz"
  version "0.11.2"
  sha256 "75588926cc70885abb98761f0d36c9841166ebc3d6f22dc0a46d38d8eeb105e0"

  include Language::Python::Virtualenv

  depends_on "wxpython"
  depends_on "numpy"
  depends_on "scipy"
  depends_on "matplotlib"
  depends_on "gsl"
  # depends_on "quantities"
  depends_on "bagit"

  # resource "quantities" do
    # url "https://pypi.python.org/packages/e4/73/23dbd5482d16e6e7bac98e3998c22cbcbecf92dda447bfe1b9ea4ae1509a/quantities-0.11.1.zip"
    # md5 "f4c6287bfd2e93322b25a7c1311a0243"
  # end

  def install
      virtualenv_install_with_resources
      Dir.chdir('src/plugins/bacon/cpp/')
      system "make", "-f", "makefileMacOSX", "sciboxplugin"
    # resource("quantities").stage { system "python", *Language::Python.setup_install_args(libexec/"vendor") }
  end

  test do
    # `test do` will create, run in and delete a temporary directory.
    #
    # This test will fail and we won't accept that! It's enough to just replace
    # "false" with the main program this formula installs, but it'd be nice if you
    # were more thorough. Run the test with `brew test cscibox`. Options passed
    # to `brew install` such as `--HEAD` also need to be provided to `brew test`.
    #
    # The installed folder is not in the path, so use the entire path to any
    # executables being tested: `system "#{bin}/program", "do", "something"`.
    system "cd","src"
    system "python","cscience.py"
  end
end
