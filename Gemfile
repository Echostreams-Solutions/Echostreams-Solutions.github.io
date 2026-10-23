source "https://rubygems.org"
# github-pages pins Liquid 4.0.3, which crashes on Ruby 3.2+ (String#tainted? was removed),
# so local builds use Jekyll 4. GitHub Pages builds with its own Jekyll 3.10; this site only uses
# features common to both (collections, includes, where/sort/relative_url).
gem "jekyll", "~> 4.3"
gem "webrick"
# Ruby 3.4+/4.0 no longer bundle these.
gem "csv"
gem "base64"
gem "bigdecimal"
gem "logger"
