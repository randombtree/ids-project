#!/usr/bin/env python3
# IDS Project 2020
# Gather data from original data-sources and store it processed locally

import data.wrangler as wrangler

def main():
    wrangler.fetch_data()

if __name__ == '__main__':
    main()
