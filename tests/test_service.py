from backend.services.comparables_service import analyze_company

def analyze_apple():
    result = analyze_company("AAPL")

    if "error" in result:
        print(f"❌ error: {result['error']}")
    else:
        print("✅ success")
        print(f"found {result['comparable_count']} comparables")
        print(f"list of comparables: {result['comparables']}")
        print(f"summary of stats {result['summary_stats']}")

    return result


if __name__ == "__main__":
    analyze_apple()