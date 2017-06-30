from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup_zb import Cocktail, Base, Alcohol, User

engine = create_engine('sqlite:///cocktailcatolog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you ca
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Jane Doe", email="janedoe@gmail.com",
            id = 1,
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Create dummy user
User0 = User(name="John Doe", email="johndoe@gmail.com",
            id = 0,
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User0)
session.commit()

# Cocktail catalog
alcohol1 = Alcohol(user_id=1,
                   name="Vodka")

session.add(alcohol1)
session.commit()

cocktail1 = Cocktail(user_id=1,
                     name="SCREWDRIVER",
                     ingredients="1.5 oz Vodka, Orange Juice",
                     picture="http://cdn.liquor.com/wp-content/uploads/2012/04/10171258/screwdriver.jpg",
                     alcohol=alcohol1)

session.add(cocktail1)
session.commit()

cocktail2 = Cocktail(user_id=1,
                     name="GYPSY QUEEN",
                     ingredients="2 oz Russian Standard Vodka, 1 oz Benedictine, 2 dashes Angostura bitters",
                     picture="http://cdn.liquor.com/wp-content/uploads/2012/06/gypsy-queen.jpg",
                     alcohol=alcohol1)

session.add(cocktail2)
session.commit()


cocktail3 = Cocktail(user_id=1,
                     name="CUCUMBER FIZZ",
                     ingredients="2 oz Cucumber, peeled and roughly chopped, 1 1/2 oz Grey Goose La Poire flavored vodka, 1/2 oz St-Germain elderflower liqueur, 1/2 oz Lemon Juice, 1/2 oz Simple syrup, Lemonade or club soda",
                     picture="http://cdn.liquor.com/wp-content/uploads/2015/07/cucumber-fizz-large-1024x1024.jpg",
                     alcohol=alcohol1)

session.add(cocktail3)
session.commit()


alcohol2 = Alcohol(user_id=1,
                   name="Bourbon")

session.add(alcohol2)
session.commit()

cocktail4 = Cocktail(user_id=1,
                     name="MINT JULEP",
                     ingredients="1/4 oz Raw sugar syrup, 8  Mint Leaves, 2 oz Bourbon",
                     picture="http://cdn.liquor.com/wp-content/uploads/2013/04/Mint-Julep.jpg",
                     alcohol=alcohol2)

session.add(cocktail4)
session.commit()

cocktail5 = Cocktail(user_id=0,
                     name="Brown Derby",
                     ingredients="1 1/2 oz Bourbon, 1 oz Fresh grapefruit juice, 1/2 oz Honey syrup*",
                     picture="http://cdn.liquor.com/wp-content/uploads/2013/04/Mint-Julep.jpg",
                     alcohol=alcohol2)

session.add(cocktail5)
session.commit()

print "added cocktail items!"
