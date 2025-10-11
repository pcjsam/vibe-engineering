import typer

from mongodb import fetch_team_members

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str):
    print(f"Goodbye {name}")


@app.command()
def team():
    team_members = fetch_team_members()

    if not team_members:
        print("No team members found.")
        return

    print(f"\nTeam Members ({len(team_members)}):")
    print("=" * 30)
    for i, member in enumerate(team_members, 1):
        print(f"  {i}. {member}")


if __name__ == "__main__":
    app()
