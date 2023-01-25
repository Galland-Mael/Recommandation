def split_string(string):
    # Split the string based on space delimiter
    list_string = string.split(',')

    return list_string

def insertresto():
    url = "https://qghub.cloud/assets/yelp_business.json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0

    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        check = False
        categories = obj.get('categories')
        city = obj.get('city')
        if categories is not None:
            liste = split_string(categories)
            size = len(liste)
            for i in range(size):
                if i != 0:  # test pour suppression de l'espace devant la chaine
                    alias = liste[i][1:]
                    liste[i] = alias
                else:
                    alias = liste[i]
                if alias.lower() == "restaurants":
                    check = True
        exist=False
        tmp2=0
        if check:
            nb = len(liste)
            for a in range(nb):
                alias = liste[a]
                tmp2 = RestaurantType.objects.filter(nom=alias.lower()).count()
                if tmp2 > 0:
                    exist=True


            if exist:
                id_yelp = obj.get('business_id')
                name = obj.get('name')
                address = obj.get('address')
                zip_code = obj.get('postal_code')
                state = obj.get('state')
                latitude = obj.get('latitude')
                longitude = obj.get('longitude')
                rating = obj.get('stars')
                nb_review = obj.get('review_count')

                restaurant = Restaurant(id_yelp=id_yelp, nom=name, adresse=address, ville=city, zip_code=zip_code,
                                        etat=state, latitude=latitude, longitude=longitude,
                                        note=rating, nb_review=nb_review)
                restaurant.save()

                liste.remove('Restaurants')
                try:
                    liste.remove('Food')
                except:
                    print('no food')

                nb = len(liste)
                for a in range(nb):
                    alias = liste[a]
                    tmp = RestaurantType.objects.filter(nom=alias.lower())
                    if tmp:
                        restaurant.type.add(tmp[0])
        print(verif)

def inserttype():
    url = "https://qghub.cloud/assets/yelp_business.json"
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    verif = 0

    # read json from url in stream
    for obj in StreamJson(req):
        verif += 1
        check = False
        categories = obj.get('categories')
        if categories is not None:
            liste = split_string(categories)
            size = len(liste)
            for i in range(size):
                if i != 0:  # test pour suppression de l'espace devant la chaine
                    alias = liste[i][1:]
                else:
                    alias = liste[i]
                if alias.lower() == "restaurants":
                    check = True

            if check:
                for j in range(size):
                    if j != 0:  # test pour suppression de l'espace devant la chaine
                        alias = liste[j][1:]
                        nb = RestaurantType.objects.filter(nom=alias.lower()).count()
                        if nb == 0:
                            b = RestaurantType(nom=alias.lower())
                            b.save()
                    else:
                        alias = liste[j]

def insert_nom():
    list = getFirstElement()
    random.shuffle(list)
    i = 0
    for personne in Adherant.objects.all():
        tmp = list[i].lower()
        tmp = tmp[0].upper() + tmp[1:]
        print(tmp)
        Adherant.objects.filter(pk=personne.pk).update(nom=tmp)
        Adherant.objects.filter(pk=personne.pk).update(
            mail=personne.prenom.lower() + "." + list[i].lower() + "@eatadvisor.com")
        i += 1
        print(i)

def setVille():
    for user in Adherant.objects.all():
        dico = {"Philadelphia": 0, "Tampa": 0, "Indianapolis": 0, "Nashville": 0, "Tucson": 0, "New Orleans": 0,
                "Saint Louis": 0, "Edmonton": 0, "Reno": 0, "Saint Petersburg": 0, "Boise": 0, "Santa Barbara": 0,
                "Clearwater": 0, "Wilmington": 0, "Metairie": 0, "Franklin": 0}
        for avis in Avis.objects.filter(adherant_fk=user):
            str_ville = str(avis.restaurant_fk.ville)
            if str_ville in dico.keys():
                dico[str_ville] += 1
        max_elem = max(dico, key=dico.get)
        Adherant.objects.filter(pk=user.pk).update(ville=max_elem)

def create_password():
    for user in Adherant.objects.all():
        mdp = user.prenom.lower() + user.nom.lower()
        hashed_password = hashlib.sha256(mdp.encode('utf-8')).hexdigest()
        Adherant.objects.filter(pk=user.pk).update(password=hashed_password)

def supplettreUTF():
    """

    @return:
    """
    for resto in Restaurant.objects.all():
        nouveau_nom = testNomUTF(resto.nom)
        if (nouveau_nom != resto.nom):
            Restaurant.objects.filter(id_yelp=resto.id_yelp).update(nom=nouveau_nom)

def testNomUTF(nom):
    """

    @param nom:
    @return:
    """
    list = "azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN0123456789&'-_+/:,*²#|!?°. "
    nouveau_nom = ""
    for lettre in nom:
        if lettre in list:
            nouveau_nom += lettre
        elif lettre in 'éèê':
            nouveau_nom += 'e'
        elif lettre in 'ÉÈ':
            nouveau_nom += 'E'
    return nouveau_nom

def calculNb_reviewAdherent():
    for adherent in Adherant.objects.all():
        somme = Avis.objects.filter(adherent_fk=adherent.pk).count()
        Adherant.objects.filter(pk=adherent.pk).update(nb_review=somme)

def calculNb_reviewRestaurant():
    for resto in Restaurant.objects.all():
        somme = Avis.objects.filter(restaurant_fk=resto.pk).count()
        Restaurant.objects.filter(pk=resto.pk).update(nb_review=somme)
       
def suppressionAdherant(nb=20):
    """
    @param nb: nombre d'avis minimum pour garder l'adhérant dans la bd
    @return: /
    """
    compteur = 0
    for adherant in Adherant.objects.all():
        if Avis.objects.filter(adherant_fk=adherant).count() < nb:
            adherant.delete()
        compteur+=1
        if compteur%1000 == 0:
            print(compteur)

def suppVille():
    listVilles = ["Philadelphia","Tampa","Indianapolis","Nashville","Tucson","New Orleans","Edmonton","Saint Louis","Reno",
                  "Saint Petersburg","Boise", "Santa Barbara","Clearwater","Wilmington","St. Louis","Metairie","Franklin"]
    Restaurant.objects.all().exclude(ville__in=listVilles).delete()

def setVille():
    listVilles = ["Philadelphia", "Tampa", "Indianapolis", "Nashville", "Tucson", "New Orleans", "Edmonton",
                  "Saint Louis", "Reno",
                  "Saint Petersburg", "Boise", "Santa Barbara", "Clearwater", "Wilmington", "St. Louis", "Metairie",
                  "Franklin"]
    print("Arrivée dans la boucle")
    for user in Adherant.objects.all():
        dico = {"Philadelphia" : 0, "Tampa" : 0, "Indianapolis" : 0, "Nashville" : 0, "Tucson" : 0, "New Orleans" : 0,
                "Edmonton" :0, "Saint Louis" : 0, "Reno" : 0, "Saint Petersburg" : 0, "Boise" : 0, "Santa Barbara" : 0,
                "Clearwater" : 0, "Wilmington" : 0, "St. Louis" : 0, "Metairie" : 0, "Franklin" : 0}
        for avis in Avis.objects.filter(adherant_fk=user):
            str_ville = str(avis.restaurant_fk.ville)
            if str_ville in dico.keys():
                dico[str_ville] += 1
        print(dico)
        return