# Documentation: https://github.com/Homebrew/brew/blob/master/share/doc/homebrew/Formula-Cookbook.md
#                http://www.rubydoc.info/github/Homebrew/brew/master/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!

class Cscibox < Formula
  desc "Geography Core Data Application"
  homepage "http://www.cs.colorado.edu/~lizb/cscience.html"
  url "https://github.com/ldevesine/cscibox/archive/0.11.3.tar.gz"
  version "0.11.3"
  sha256 "014d289bbb28a11940388645976cf92ea7d104d14cdf666de50cbc43307670e7"

  include Language::Python::Virtualenv

  depends_on "wxpython"
  depends_on "gsl"

  def install
      virtualenv_install_with_resources
      Dir.chdir('src/plugins/bacon/cpp/')
      system "make", "-f", "makefileMacOSX", "sciboxplugin"
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
