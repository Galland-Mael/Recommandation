import os
import sys


def generate_html_docs(app_path, output_dir):
    """
    genere l'ensemble des fichiers html de la pydoc
    @param app_path:
    @param output_dir:
    @return:
    """
    sys.path.insert(0, app_path)
    os.chdir(output_dir)

    modules = [
        "appsae.__init__.py",
        "appsae.admin.py",
        "appsae.ajoutRecoBd.py",
        "appsae.apps.py",
        "appsae.asgi.py",
        "appsae.fonctionsBd.py",
        "appsae.formulaire.py",
        "appsae.generateDoc.py",
        "appsae.gestion.py",
        "appsae.gestion_groupes.py",
        "appsae.gestion_note.py",
        "appsae.gestion_utilisateur.py",
        "appsae.listeRecommandation.py",
        "appsae.models.py",
        "appsae.recommandation_groupe.py",
        "appsae.recommendation.py",
        "appsae.settings.py",
        "appsae.svd.py",
        "appsae.urls.py",
        "appsae.views.py",
        "appsae.wsgi.py"
    ]

    for module in modules:
        os.system(f"pydoc -w {module}")
        print("generated " + module)

    print("HTML documentation generated successfully!")
