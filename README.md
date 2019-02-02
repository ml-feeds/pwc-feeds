# pwc-feeds
**pwc-feeds** uses Python 3.7 to serve RSS feeds for Papers With Code. 
As a disclaimer, it has no affiliation with Papers With Code.

## Links
* [Project repo](https://github.com/ml-feeds/pwc-feeds)
* Original HTML listing: [Trending](https://paperswithcode.com/) | [Latest](https://paperswithcode.com/latest) | [Greatest](https://paperswithcode.com/greatest)
* **Unofficial RSS feeds: [Trending](https://us-east1-ml-feeds.cloudfunctions.net/pwc/trending) | [Latest](https://us-east1-ml-feeds.cloudfunctions.net/pwc/latest) | [Greatest](https://us-east1-ml-feeds.cloudfunctions.net/pwc/greatest)**

## Deployment
Serverless deployment to [Google Cloud Functions](https://console.cloud.google.com/functions/) is configured.
It requires the the following files:
* requirements.txt
* main.py (having callable `serve(request: flask.Request) -> Tuple[Union[bytes, str], int, Dict[str, str]]`)

Deployment version updates are not automated.
They can be performed manually by editing and saving the function configuration.

These deployment links require access:
* [Dashboard](https://console.cloud.google.com/functions/details/us-east1/pwc?project=ml-feeds)
* [Logs](https://console.cloud.google.com/logs?service=cloudfunctions.googleapis.com&key1=pwc&key2=us-east1&project=ml-feeds)
* [Repo](https://source.cloud.google.com/ml-feeds/github_ml-feeds_pwc-feeds)
