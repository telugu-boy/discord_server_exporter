"""
    Discord Server Exporter - exports and import servers as json
    Copyright (C) 2021 telugu_boy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import logging
from urllib.request import Request, urlopen

# This header is needed or else we get 403 forbidden '-'
# The user agent and accept* are copied from a random Chrome request
req_hdr = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

# emoji slot count lookup table
boost_emoji_count = {0: 50, 1: 100, 2: 150, 3: 250}


"""
Gets a server icon under 10mb if the original is over

Return: bytes-like object with the downloaded icon

Arguments:
    url -- URL to the server icon
"""


def get_icon_under_10mb(url: str):
    icon_sizes = (2048, 1024, 512, 256, 128)

    # Sorted in ascending order of size.  GIFs are added to the front
    # if the supplied URL points to a GIF.
    formats = ["webp", "jpg", "png"]

    # to determine if GIF or not
    # Icons are of the format `URL.ext?size=xxx`
    # after the last dot and before the first exclamation mark is
    # where the extension lies.
    icon_ext = url.split(".")[-1].split("?")[0]

    # GIFs are not processed for non animated icons, so accessing it would give
    # an error
    if icon_ext == "gif":
        formats.insert(0, "gif")

    # The URL without an extension or size.
    icon_url_no_ext = ".".join(url.split(".")[:-1])

    # Try original first
    req = Request(url, None, req_hdr)
    server_icon_req = urlopen(req)

    # file cannot be larger than 10240.0 kb
    if int(server_icon_req.info()["Content-Length"]) > 10240000:
        logging.warning(
            "Original server icon larger than 10.240MB limit. Searching for smaller..."
        )
    else:
        return server_icon_req.read(), icon_ext

    # We want the highest resolution images, so try 2048 on all formats and
    # then the next highest size 1024 and so on
    for icon_size in icon_sizes:
        for format in formats:
            logging.info(f"Trying {format} and {icon_size}")

            candidate_icon_url = f"{icon_url_no_ext}.{format}?size={icon_size}"
            req = Request(candidate_icon_url, None, req_hdr)
            server_icon_req = urlopen(req)

            file_size = int(server_icon_req.info()["Content-Length"])
            # not <= just to be safe '-'
            if file_size < 10240000:
                logging.info(
                    f"Found suitable icon with extension {format}, resolution {icon_size} ({file_size}b)"
                )
                return server_icon_req.read(), icon_ext