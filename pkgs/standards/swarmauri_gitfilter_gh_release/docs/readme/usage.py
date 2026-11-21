from swarmauri_gitfilter_gh_release import GithubReleaseFilter

filt = GithubReleaseFilter.from_uri("ghrel://org/repo/tag/artifacts")

print(filt.root_uri)
