from bs4 import BeautifulSoup

__url = "https://www.sf4-industry.com"


def build_search_requests(core, service_name, meta):
    if meta.is_movie:
        query = meta.title + " " + meta.year if meta.year else ""
        search_type = 1
    else:
        query = f"{meta.tvshow} S{meta.season:>02}E{meta.episode:>02}"
        search_type = 2

    params = {"search": query, "searchType": search_type}

    request = {"method": "GET", "url": f"{__url}/search_report.php", "params": params}

    meta.languages.append("Greek")

    return [request]


def parse_tvseries(soup):
    subs = []
    subtitle_elements = soup.select(".page_header table tr:nth-child(2) td table")
    for element in subtitle_elements:
        if not element.findChild("img") or "gif" not in element.findChild("img")["src"]:
            continue
        lang = "Greek" if "el" in element.findChild("img")["src"] else "English"
        url = __url + element.findChild("a")["href"]
        name = element.findChild("a")["title"]
        subs.append({"lang": lang, "name": name, "url": url})
    return subs


def parse_movies(soup):
    subs = []

    # Find and iterate over the relevant HTML elements
    subtitle_elements = soup.find_all("div", {"class": "movie-details"})
    for element in subtitle_elements:
        lang = "Greek" if element.findChild("div", {"class": "elgif"}) else "English"
        name = element.findChild("a")["title"]
        url = __url + element.findChild("a")["href"]
        subs.append({"lang": lang, "name": name, "url": url})
    return subs


def parse_search_response(core, service_name, meta, response):
    service = core.services[service_name]

    soup = BeautifulSoup(response.content, "html.parser")

    # Initialize the list to hold subtitles
    subs = []

    # Find and iterate over the relevant HTML elements
    subtitle_elements = parse_movies(soup) if meta.is_movie else parse_tvseries(soup)
    for element in subtitle_elements:

        sub = {
            "service_name": service_name,
            "service": service.display_name,
            "lang": element["lang"],
            "lang_code": core.kodi.xbmc.convertLanguage(
                element["lang"], core.kodi.xbmc.ISO_639_1
            ),
            "name": element["name"],
            "rating": 0,
            "url": element["url"],
            "sync": "false",
            "impaired": "false",
            "color": "orange",
            "action_args": {
                "url": element["url"],
                "lang": element["lang"],
                "filename": element["name"],
                "raw": True,
            },
        }
        subs.append(sub)

    return subs


def build_download_request(core, service_name, args):
    request = {"method": "GET", "url": args["url"]}

    return request
