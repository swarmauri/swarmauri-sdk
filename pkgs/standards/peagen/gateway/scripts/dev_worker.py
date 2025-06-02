import os, argparse, uvicorn

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gw", default="http://localhost:8000/rpc")
    ap.add_argument("--pool", default="default")
    ap.add_argument("--port", default=9001, type=int)
    args = ap.parse_args()

    os.environ["DQ_GATEWAY"] = args.gw
    os.environ["DQ_POOL"] = args.pool
    os.environ["PORT"]   = str(args.port)

    uvicorn.run(
        "dqueue.worker.server:app",
        host="0.0.0.0",
        port=args.port,
        reload=True,
        log_level="info",
    )

if __name__ == "__main__":
    main()
