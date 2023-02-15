# Copyright (c) 2023 Blacknon. All rights reserved.
# Use of this source code is governed by an MIT license
# that can be found in the LICENSE file.
# =======================================================

FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

# apt update
RUN apt update

# apt install
RUN apt install -y \
    firefox-esr \
    chrome \
    python3-pip

# copy directory
COPY ./ /opt/pydork
WORKDIR /opt/pydork

# listing /opt/pydork
RUN ls -la /opt/pydork

# # pip install
RUN pip3 install ./
