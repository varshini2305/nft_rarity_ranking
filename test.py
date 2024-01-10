# python test.py
import argparse

# Command line argument parser
parser = argparse.ArgumentParser(description="Parallel script for fetching data.")
parser.add_argument("--start", type=int, help="Start index or position in the list", default=0)
parser.add_argument("--size", type=int, help="No of urls ot fetch for", default=1500000)
parser.add_argument("--batch_size", type=int, help="Batch size for writing output files", default=100)
# parser.add_argument("--output_path", type=str, help="Custom output path for data files", default="data/")



args = parser.parse_args()


output = f"data/aggregated_nfts_df_{args.start}_{args.start+args.size}.pkl"
print(f"{output=}")