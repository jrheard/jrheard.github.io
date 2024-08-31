# file copy-pasted wholesale from http://ixti.net/software/2013/01/28/using-jekyll-plugins-on-github-pages.html
require "rubygems"
require "tmpdir"

require "bundler/setup"
require "jekyll"

# TODO rewrite in cljs/planck for funsies

GITHUB_REPONAME = "jrheard/jrheard.github.io"

desc "Generate blog files"
task :generate do
  Jekyll::Site.new(Jekyll.configuration({
    "source"      => ".",
    "destination" => "_site"
  })).process
end


desc "Generate and publish blog to gh-pages"
task :publish => [:generate] do
  Dir.mktmpdir do |tmp|
    cp_r "_site/.", tmp

    pwd = Dir.pwd
    Dir.chdir tmp

    system "git init"
    system "git checkout -b master"
    system "git add ."
    message = "Site updated at #{Time.now.utc}"
    system "git commit -m #{message.inspect}"
    system "git remote add origin git@github.com:#{GITHUB_REPONAME}.git"
    system "git push origin master --force"

    Dir.chdir pwd
  end
end
