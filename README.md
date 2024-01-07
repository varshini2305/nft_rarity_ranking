### Fetching Rarity Ranks of NFTs within each collection - identified by Contract address / Collection Slug

#### Rarity Sniper - contains rarity ranks and rarity scores at a NFT level, within each collection, which can be directly fetched.

#### Opensea - can be used to fetch collection-level stats


- NFT metadata can be fetched using Rarity Sniper including collection size (total no. of NFTs within collection) and NFT level stats (like rarity score, rarity rank)

```
https://raritysniper.com/robots.txt
```

Below displays crawling permissions, which is fully allowed for rarity sniper.

```
User-agent: *
Allow: /
Sitemap: https://raritysniper.com/sitemap
Sitemap: https://raritysniper.com/news/sitemap.xml
Sitemap: https://raritysniper.com/news/sitemap-news.xml
```

- Opensea - was used to initially fetch collection-level stats

- NFT Rarity ranks can also be computed based on custom heuristics, loosely based on existing methods like trait value based rarity scoring, inversely proportional to rarity ranking


```
[Rarity Score for a Trait Value] = 1 / ([Number of Items with that Trait Value] / [Total Number of Items in Collection])

The total Rarity Score for an NFT is the sum of the Rarity Score of all of it’s trait values.

[Rarity Score for a Trait Value] = 1 / [Trait Rarity of that Trait Value]
```

[Ranking Rarity: Understanding Rarity Calculation Methods](https://raritytools.medium.com/ranking-rarity-understanding-rarity-calculation-methods-86ceaeb9b98c)


##### Input data - data/Collections.csv

- Output files - nftd_data_latest.pkl, data_collection_stats.pkl can be found below

[Output files ](https://drive.google.com/drive/folders/1EZfFEajrYSvyTm89OOFjIpRzs177Stbh?usp=drive_link)

##### Output data - nfts_df.pkl, - nfdf.columns = collection_slug', 'nft_id', 'rank', 'rarityScore', 'image', 'traits'

##### nfts_data_latest.pkl - contains latest status of rarity meta for 364500 NFTs, as the script takes a few more hours to fetch for all ~45L unique NFTs from all the given collections.

Example record - 

```
{'rank': 525,
 'rarityScore': 4351.34,
 'image': 'https://ipfs.io/ipfs/QmZVk9ngMpxq1FoQcFrSXMPgy7rXXFzqcSSik6C7PoCjbx/9.png',
 'traits': [{'count': 5,
   'percent': 0.5,
   'traitType': 'Weapon',
   'traitValue': 'Snally Eye',
   'rarityScore': 2191.16},
  {'count': 140,
   'percent': 14.03,
   'traitType': 'Traits Count',
   'traitValue': '6',
   'rarityScore': 503.07},
  {'count': 36,
   'percent': 3.61,
   'traitType': 'Background',
   'traitValue': 'Sky Noon C',
   'rarityScore': 402.79},
  {'count': 167,
   'percent': 16.73,
   'traitType': 'Faction',
   'traitValue': 'Wiz',
   rarityScore': 328.02}
 ]
}
```

Collection level stats fetched using Opensea - data/collection_stats.pkl

```
Example record -

{'collection_slug': 'bearsontheblock',
 'collection_stats': {'total': {'volume': 11.23,
   'sales': 25,
   'average_price': 0.44920000000000004,
   'num_owners': 128,
   'market_cap': 0.0,
   'floor_price': 0.0,
   'floor_price_symbol': ''},
  'intervals': [{'interval': 'one_day',
    'volume': 0.0,
    'volume_diff': 0.0,
    'volume_change': 0.0,
    'sales': 0,
    'sales_diff': 0.0,
    'average_price': 0.0},
   {'interval': 'seven_day',
    'volume': 0.0,
    'volume_diff': 0.0,
    'volume_change': 0.0,
    'sales': 0,
    'sales_diff': 0.0,
    'average_price': 0.0},
   {'interval': 'thirty_day',
    'volume': 0.0,
    'volume_diff': 0.0,
    'volume_change': 0.0,
    'sales': 0,
    'sales_diff': 0.0,
    'average_price': 0.0}]}}
    ```