import pandas as pd
import asyncio
import aiohttp
import logging
import argparse
from tqdm import tqdm

from functools import lru_cache

# Read the dataframe from pickle file
# url_df = pd.read_pickle("data/url_df.pkl")
# urls = url_df.values.tolist()

# remaining_urls_df = pd.read_pickle("data/remaining_urls_df.pkl")
remaining_urls_df = pd.read_pickle('data/batch_3_urls.pkl')


urls = remaining_urls_df[['nft_id', 'collection_slug', 'url']].values.tolist()


# Command line argument parser
parser = argparse.ArgumentParser(description="Parallel script for fetching data.")
parser.add_argument("--start", type=int, help="Start index or position in the list", default=0)
parser.add_argument("--size", type=int, help="No of urls ot fetch for", default=len(urls))
parser.add_argument("--batch_size", type=int, help="Batch size for writing output files", default=100)
# parser.add_argument("--output_path", type=str, help="Custom output path for data files", default="data/")



args = parser.parse_args()


# Extract relevant URLs based on start and stop indices
selected_urls = urls[args.start:args.start+args.size]

print(f"{len(urls)=}, {len(selected_urls)=}, {args.size=}, {args.start=}, args.end={args.start+args.size}")

# Initialize global variables
count = 0
payload = {}
headers = {
    'authority': 'api.raritysniper.com',
    'accept': 'application/json',
    'origin': 'https://raritysniper.com'
}

nfts_list = []
nfts_df = pd.DataFrame()

@lru_cache(maxsize=None)
async def fetch_data(session, url, collection_slug, i, progress_bar):
    global count
    response = await session.get(url, headers=headers, data=payload)
    resp = await response.json()
    subset_dict = {key: resp[key] for key in ['rank', 'rarityScore', 'image', 'traits']}
    subset_dict['collection_slug'] = collection_slug
    subset_dict['nft_id'] = i
    nfts_list.append(subset_dict)

    global count
    global nfts_df
    count += 1

    progress_bar.update(1)
    # print(f"{count=}")
    try:
        if count % args.batch_size == 0:
            prev_filename = f"data/prev_nfts_df_{args.start}_{args.start+args.size}.pkl"
            
            if nfts_df.empty is False:
                print(f"updating {prev_filename=}, {len(nfts_list)=}")
                nfts_df.to_pickle(f"data/prev_nfts_df_{args.start}_{args.start+args.size}.pkl")

            current_filename = f"data/nfts_df_{args.start}_{args.start+args.size}.pkl"
            nfts_df = pd.DataFrame(nfts_list)

            print(f"writing to {current_filename=}")
            nfts_df.to_pickle(current_filename)

    except Exception as e:
        print("exception")
        logging.exception(f"traceback as follows...{count=}, {len(nfts_list)=}")


async def bound_fetch(sem, func):
    async with sem:
        return await func

max_concurrent_requests = 15

async def main():
    async with aiohttp.ClientSession() as session:
        with tqdm(total=len(selected_urls)) as progress_bar:
            tasks = [fetch_data(session, url, cs, i, progress_bar) for i, cs, url in selected_urls]
            semaphore = asyncio.Semaphore(max_concurrent_requests)
            tasks = [bound_fetch(semaphore, fetch_data(session, url, collection_slug, i, progress_bar)) for i, collection_slug, url in selected_urls]
            await asyncio.gather(*tasks, return_exceptions=True)
            nfts_df = pd.DataFrame()
            try:
                # Save the final batch if not a multiple of batch size
                if nfts_list:
                    nfts_df = pd.DataFrame(nfts_list)
                    final_filename = f"data/aggregated_nfts_df_{args.start}_{args.start+args.size}.pkl"        
                    nfts_df.to_pickle(final_filename)
            except KeyboardInterrupt:
                try:    
                    final_filename = f"data/aggregated_nfts_df_{args.start}_{args.start+args.size}.pkl"        
                    print(f"process interrupted, writing until - {count=}, f{len(nfts_list)=} to {final_filename=}")
                    nfts_df.to_pickle(final_filename)
                except Exception:
                    logging.exception("traceback as follows")
                    print("failed writing contents to the file")
            except Exception:
                logging.exception("traceback as follows")
                try:    
                    final_filename = f"data/aggregated_nfts_df_{args.start}_{args.start+args.size}.pkl"        
                    print(f"process interrupted, writing until - {count=}, f{len(nfts_list)=} to {final_filename=}")
                    nfts_df.to_pickle(final_filename)
                except Exception:
                    logging.exception("traceback as follows")
                    print("failed writing contents to the file")

if __name__ == "__main__":
    asyncio.run(main())


# python run_batches.py --start 0 --size 1500000 --batch_size 1000
# python run_batches.py --start 1500000 --size 1500000 --batch_size 1000