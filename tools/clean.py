#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#
#  Copyright (C) 2013 Neil MacLeod (texturecache@nmacleod.com)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Simple utility to match artwork url patterns and generate work items to
# remove (clean) those items from the XBMC media library.
#
# https://github.com/MilhouseVH/texturecache.py/blob/master/tools/clean.py
#
# Usage:
#
#  ./texturecache.py jd movies | ./clean.py pattern [pattern]*
#
# eg.
#
#  ./texturecache.py jd movies  | ./clean.py /movielogo/-51fd12c146bd9\.png
#  ./texturecache.py jd movies  | ./clean.py /moviethumb/ /moviedisc/ /moviebanner/
#  ./texturecache.py jd tvshows | ./clean.py assets\.fanart\.tv
#
################################################################################

#version 0.1.0

from __future__ import print_function
import sys, os, codecs, json, re

def init():
  if sys.version_info >= (3, 1):
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
  else:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr)

def getdata():
  data=[]
  for line in sys.stdin: data.append(line)
  jdata = json.loads("".join(data))
  del data
  return jdata

def processitems(data, patterns):
  workitems=[]

  for item in data:
    items = {}
    for a in item.get("art", []):
      if not a.startswith("tvshow."):
        url = re.sub("^image://(.*)/", "\\1", item["art"][a])
        for pattern in patterns:
          if pattern.search(url):
            items["art.%s" % a] = None

    if items:
      if "movieid" in item:
        workitems.append({"items": items, "libraryid": item["movieid"], "type": "movie", "title": item["title"]})
      elif "tvshowid" in item:
        workitems.append({"items": items, "libraryid": item["tvshowid"], "type": "tvshow", "title": item["title"]})
      elif "seasonid" in item:
        workitems.append({"items": items, "libraryid": item["seasonid"], "type": "season", "title": item["label"]})
      elif "episodeid" in item:
        workitems.append({"items": items, "libraryid": item["episodeid"], "type": "episode", "title": item["label"]})

    if "seasons" in item:  workitems.extend(processitems(item["seasons"], patterns))
    if "episodes" in item: workitems.extend(processitems(item["episodes"], patterns))

  return workitems

def main(args):
  init()

  patterns = []

  # If no args, default to a logo pattern that is erroneously
  # added by Artwork Downloader
  if not args:
    args.append("/movielogo/-51fd12c146bd9\.png")

  for arg in args:
    patterns.append(re.compile(arg))

  workitems = processitems(getdata(), patterns)

  sys.stdout.write(json.dumps(workitems, indent=2))
  sys.stdout.write("\n")
  sys.stdout.flush()

try:
  main(sys.argv[1:])
except (KeyboardInterrupt, SystemExit) as e:
  if type(e) == SystemExit: sys.exit(int(str(e)))
