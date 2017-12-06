from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog_db import User, Base, CatalogCategory, CategoryItem
engine = create_engine('sqlite:///catalog_app.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user = User(name="Gustavo Smaniotto", email="ghsmaniotto@gmail.com")
session.add(user)
session.commit()

category1 = CatalogCategory(name="Website", user=user)
session.add(category1)
session.commit()

item1 = CategoryItem(name="Forum website", catalog_category=category1, description="A site where people can hold conversations in the form of posted messages.", user=user)
session.add(item1)
session.commit()

item2 = CategoryItem(name="Webmail", catalog_category=category1, description="A site that provides a webmail service.", user=user)
session.add(item2)
session.commit()

category2 = CatalogCategory(name="Football", user=user)
session.add(category2)
session.commit()

item3 = CategoryItem(name="American Football", 
		catalog_category=category2, 
		description="""American football, referred to as football in the United States and Canada, and also known as "gridiron football" or simply "gridiron", is a sport played by two teams of eleven players on a rectangular field with goalposts at each end. The offense, the team with control of the oval-shaped football, attempts to advance down the field by running with or passing the ball, while the team without control of the ball, the defense, aims to stop their advance and take control of the ball for themselves. The offense must advance at least ten yards in four downs, or plays, or else they turn over the football to the opposing team; if they succeed, they are given a new set of four downs. Points are primarily scored by advancing the ball into the opposing team's end zone for a touchdown or kicking the ball through the opponent's goalposts for a field goal. The team with the most points at the end of a game wins.""", 
		user=user)
session.add(item3)
session.commit()

item4 = CategoryItem(name="Futsal", 
		catalog_category=category2 ,
		description="""Futsal is a variant of association football played on a hard court, smaller than a football pitch, and mainly indoors. It can be considered a version of five-a-side football.""",
		user=user)
session.add(item4)
session.commit()

item5 = CategoryItem(name="Association football",
		catalog_category=category2, 
		description=""" Association football, more commonly known as football or soccer, is a team sport played between two teams of eleven players with a spherical ball. It is played by 250 million players in over 200 countries and dependencies, making it the world's most popular sport. The game is played on a rectangular field with a goal at each end. The object of the game is to score by getting the ball into the opposing goal.""",
		user=user)
session.add(item5)
session.commit()

category3 = CatalogCategory(name="University", user=user)
session.add(category3)
session.commit()

item6 = CategoryItem(name="Medieval universities", 
		catalog_category=category3, 
		description="""A medieval university is a corporation organized during the High Middle Ages for the purposes of higher learning. The first Western European institutions generally considered to be universities were established in the Kingdom of Italy, then part of the Holy Roman Empire, the Kingdom of England, the Kingdom of France, the Kingdom of Spain, and the Kingdom of Portugal between the 11th and 15th centuries for the study of the Arts and the higher disciplines of Theology, Law, and Medicine. These universities evolved from much older Christian cathedral schools and monastic schools, and it is difficult to define the exact date at which they became true universities, although the lists of studia generalia for higher education in Europe held by the Vatican are a useful guide.""", 
		user=user)
session.add(item6)
session.commit()

item7 = CategoryItem(name="Modern universities", 
		catalog_category=category3, 
		description="""By the 18th century, universities published their own research journals and by the 19th century, the German and the French university models had arisen. The German, or Humboldtian model, was conceived by Wilhelm von Humboldt and based on Friedrich Schleiermacher's liberal ideas pertaining to the importance of freedom, seminars, and laboratories in universities. The French university model involved strict discipline and control over every aspect of the university.""", 
		user=user)
session.add(item7)
session.commit()

category4 = CatalogCategory(name="Family", user=user)
session.add(category4)
session.commit()

item9 = CategoryItem(name="Conjugal (nuclear or single) family", 
		catalog_category=category4, 
		description="""The term "nuclear family" is commonly used, especially in the United States of America, to refer to conjugal families. A "conjugal" family includes only the husband, the wife, and unmarried children who are not of age. Sociologists distinguish between conjugal families (relatively independent of the kindred of the parents and of other families in general) and nuclear families (which maintain relatively close ties with their kindred).[citation needed] Other family structures, such as blended parents, single parents, and domestic partnerships have begun to challenge the normality of the nuclear family.""", 
		user=user)
session.add(item9)
session.commit()

item10 = CategoryItem(name="Matrifocal family", 
		catalog_category=category4, 
		description="""A "matrifocal" family consists of a mother and her children. Generally, these children are her biological offspring, although adoption of children is a practice in nearly every society. This kind of family occurs commonly where women have the resources to rear their children by themselves, or where men are more mobile than women. As a definition, "a family or domestic group is matrifocal when it is centred on a woman and her children. In this case, the father(s) of these children are intermittently present in the life of the group and occupy a secondary place. The children's mother is not necessarily the wife of one of the children's fathers.""", 
		user=user)
session.add(item10)
session.commit()

print "added menu items!"
