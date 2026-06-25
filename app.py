from fastapi import FastAPI

app = FastAPI(title="KPT AI Manager")


@app.get("/")
def root():
    return {
        "service": "KPT AI Manager",
        "status": "running"
    }
