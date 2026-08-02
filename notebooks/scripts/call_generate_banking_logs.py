import generate_banking_logs

if __name__ == "__main__":
    df = generate_banking_logs.main()
    print(df.head())
