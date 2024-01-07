import requests
import yaml
import pandas as pd
import numpy as np
import ast
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import asyncio
import aiohttp
import multiprocessing

import nest_asyncio
nest_asyncio.apply()


with open('config/config.yaml') as f:
    config  = yaml.safe_load(f)

data = pd.read_csv("data/Collections_Assignment.csv")

data.columns = ['contract_address', 'collection_slug']

# getting the unique collection slugs 

collection_slugs = list(data['collection_slug'].drop_duplicates().to_numpy())

url = "https://api.opensea.io/api/v2/traits/collection_slug"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)




# fetching collection wise stats
def collection_stats(cs):
    url = f"https://api.opensea.io/api/v2/collections/{cs}/stats"
    headers = {"accept": "application/json", "X-API-KEY": API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def fetch_collection_stats(collection_slugs: list):
    collection_stats = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:  # You can adjust max_workers as needed
            futures = [executor.submit(fetch_collection_stats, cs) for cs in collection_slugs]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching Collection Stats"):
                result = future.result()
                collection_stats.append(result)
                time.sleep(1)  # Add a delay between requests to avoid rate limiting
    
    collection_stats_df = pd.DataFrame({'collection_slug': collection_slugs, 'collection_stats': collection_stats})
    collection_stats_df.to_pickle("data/collection_stats_df.pkl")

    data_collection_stats = data.merge(collection_stats_df, on = 'collection_slug')
    data_collection_stats.columns = ['contract_address', 'collection_slug', 'collection_stats']
    data_collection_stats = data_collection_stats[['collection_slug', 'contract_address', 'collection_stats']]
    data_collection_stats.to_pickle("data/data_collection_stats.pkl")



payload = {}
headers = {
  'Referer': 'https://raritysniper.com/'
}

def size_of_collection(collection_slug):
    url = f"https://api.raritysniper.com/public/collection/{collection_slug}"


    response = requests.request("GET", url, headers=headers, data=payload)

    resp = response.json()
    
    try:

        collection_size = resp['totalSupply']
    except Exception:
        collection_size = 0

    return collection_size

data = pd.read_pickle("data/data_collection_stats.pkl")

collection_slugs = list(data['collection_slug'].drop_duplicates().to_numpy())


# generate all NFT urls to concurrently fetch their metadata - like rarity score or rarity rank, trait values, etc
# len(urls) = 4152150 - no of unique NFTs from all the given 739 collections

def generate_nft_urls(collection_slugs):
    urls = []
    for collection_slug in tqdm(collection_slugs):
        collection_size = size_of_collection(collection_slug)
        logging.info(f"collecting NFT traits for {collection_slug=},  {collection_size=}")
        
        try:
            for i in range(collection_size):
                
                url = f"https://api.raritysniper.com/public/collection/{collection_slug}/id/{i}"
                urls.append((i, collection_slug, url))
        except Exception:
            pass
    url_df = pd.DataFrame(urls)
    url_df.to_pickle("data/url_df.pkl")
    return urls


# concurrently fetching NFT wise metadata using raritysniper API
count = 0
payload = {}
headers = {
        'authority': 'api.raritysniper.com',
        'accept': 'application/json',
        'origin': 'https://raritysniper.com'
        }

nfts_list = []


# GET request is made to fetch the rarity info, including rank, score, NFT image and its traits using the collection slug, and NFT's token id
async def fetch_data(session, url, collection_slug, i, progress_bar):
    response = await session.get(url, headers=headers, data=payload)
    resp = await response.json()
    subset_dict = {key: resp[key] for key in ['rank', 'rarityScore', 'image', 'traits']}
    subset_dict['collection_slug'] = collection_slug
    subset_dict['nft_id'] = i
    nfts_list.append(subset_dict)

    global count # to consistently update the counter to track total no of NFTs info fetched during async exec
    count += 1 
    
    progress_bar.update(1)  # Update the progress bar
   
    if count % 100 == 0:
        nfts_df = pd.DataFrame(nfts_list)
        nfts_df.to_pickle("data/nfts_df.pkl") # to frequently update the NFTs metadata fetch so far.



max_concurrent_requests = 32 # multiprocessing.cpu_count() * 4


async def bound_fetch(sem, func):
    # Wrapper function to limit the number of concurrent calls
    async with sem:
        return await func

# using async API calls, execution is quicker, but the API requests count are still high - so it takes a few hrs for completion

async def main():
    async with aiohttp.ClientSession() as session:
        # Limit the number of concurrent requests using asyncio.semaphore
        with tqdm(total=len(urls)) as progress_bar:
            tasks = [fetch_data(session, url, cs, i, progress_bar) for i, cs, url in urls]
            semaphore = asyncio.Semaphore(max_concurrent_requests)
            tasks = [bound_fetch(semaphore, fetch_data(session, url, collection_slug, i, progress_bar)) for i, collection_slug, url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            pd.DataFrame(results).to_pickle("data/results.pkl")




asyncio.run(main())


# current status - 
# results = pd.read_pickle("data/nfts_df.pkl")
# (200200, 6) - 3.12 L/41 L requests complete.
# Total no of NFT Tokens combining all unique 739 collections - 4152150
