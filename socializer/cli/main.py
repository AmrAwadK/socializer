from typing import List

import typer
from dataclass_csv import DataclassWriter
from PyInquirer import prompt

from socializer.data_augmentation import GenderClassifier
from socializer.google_contacts import GoogleContactsAdapter
from socializer.google_contacts.manager import GoogleContactsManager
from socializer.google_contacts.models import GooglePerson
from socializer.models import Contact, Gender

app = typer.Typer()
gmanager = GoogleContactsManager()


def _fix_missing_genders(people: List[GooglePerson]):
    classifier = GenderClassifier()
    for person in people:
        result = classifier.classify(name=person.given_name)
        questions = [
            {
                "type": "expand",
                "message": f"Recommendation for '{person.given_name}' is '{result.gender}' ({result.probability}%)': ",
                "name": "gender",
                "default": "a",
                "choices": [
                    {"key": "a", "name": "Accept", "value": result.gender},
                    {"key": "m", "name": "Override to Male", "value": "male",},
                    {"key": "f", "name": "Override to Female", "value": "female"},
                ],
            }
        ]
        answers = prompt(questions)
        gmanager.update_gender(
            resource_name=person.resource_name,
            etag=person.etag,
            gender=Gender(answers["gender"]),
        )


def _check_missing_gender(people: List[GooglePerson]):
    missing_gender = [c for c in people if c.gender is None]
    if missing_gender:
        questions = [
            {
                "type": "confirm",
                "message": f"Found {len(missing_gender)}/{len(people)} people with missing gender, Do you want to fix them?",
                "name": "fix_missing_gender",
                "default": True,
            },
        ]
        answers = prompt(questions)
        if answers["fix_missing_gender"]:
            _fix_missing_genders(people=missing_gender)
    else:
        typer.echo("All people have gender set!")


@app.command()
def analyze_group(name: str, limit: int = 20):
    """Analyze Google Contacts Group and optionally add any missing data."""
    typer.echo(f"Analyzing contact group: {name} ...")

    people = gmanager.get_people_in_group(group_name=name, limit=limit)

    typer.echo(f"Found {len(people)} people in the group")

    _check_missing_gender(people=people)


@app.command()
def export_contacts(
    group_name: str = typer.Option(...),
    output: typer.FileTextWrite = typer.Option("contacts.csv"),
    limit: int = 20,
):
    """Export Contacts in a google contact group to a csv file."""
    gcontacts_manager = GoogleContactsAdapter()
    contacts = gcontacts_manager.get_contacts_in_group(
        group_name=group_name, limit=limit
    )

    writer = DataclassWriter(output, contacts, Contact)
    writer.write()
    typer.echo(f"contacts written to {output.name}")


if __name__ == "__main__":
    app()
