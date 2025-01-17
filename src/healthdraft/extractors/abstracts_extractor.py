import pandas as pd
from pymed import PubMed
import os
import json
from src.config import (
    get_absolute_path,
)  # will also run config.py, setting up env variables

docker = False


def fetch_from_keywords(keywords: list[str]):
    keywords = [keyword for keyword in keywords if keyword.strip()]
    if keywords is None or len(keywords) == 0:
        print("Keywords cannot be empty")
        return None

    pubmed = PubMed(tool="PubMedSearcher", email="myemail@ccc.com")

    pubmed_api_key = os.getenv("PUBMED_API_KEY")

    if pubmed_api_key is None:
        raise ValueError("API_KEY environment variable is not set")

    # Monkey patch to use api key
    pubmed.parameters.update({"api_key": pubmed_api_key})
    pubmed._rateLimit = 10

    # PUT YOUR SEARCH TERM HERE ##
    search_terms = [keyword for keyword in keywords]
    # Create a GraphQL query in plain text
    # query = '(("2018/05/01"[Date - Create] : "3000"[Date - Create])) AND (Xiaoying Xian[Author] OR diabetes)'

    articleList = []
    articleInfo = []

    for search_term in search_terms:
        results = pubmed.query(search_term, max_results=10)

        for article in results:
            # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
            # We need to convert it to dictionary with available function
            articleDict = article.toDict()
            articleList.append(articleDict)

        # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
        for article in articleList:
            # Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId
            # in that list - thats article pubmedId
            pubmedId = article["pubmed_id"].partition("\n")[0]
            # Append article info to dictionary
            articleInfo.append(
                {
                    "pubmed_id": pubmedId,
                    "title": article["title"],
                    "keywords": article["keywords"],
                    "journal": article["journal"],
                    "abstract": article["abstract"],
                    "conclusions": article["conclusions"],
                    "methods": article["methods"],
                    "results": article["results"],
                    "copyrights": article["copyrights"],
                    "doi": article["doi"],
                    "publication_date": article["publication_date"],
                    "authors": article["authors"],
                }
            )

        # Generate Pandas DataFrame from list of dictionaries
    articlesPD = pd.DataFrame.from_dict(articleInfo)
    articlesPD.drop_duplicates(subset=["doi"], inplace=True)
    return articlesPD


def main():
    keywords = ["knee", "bucket", "asthma", "diabetes"]
    articlesPD = fetch_from_keywords(keywords)

    # Saving instructions
    config_path = get_absolute_path("config.json")

    if docker:
        config_path = "/app/" + config_path

    # Lire le fichier de configuration JSON
    with open(config_path, "r") as f:
        config = json.load(f)

    abstracts_path = get_absolute_path(config.get("abstracts_output_path"))

    articlesPD.to_csv(abstracts_path, index=None, header=True)


if __name__ == "__main__":
    main()
