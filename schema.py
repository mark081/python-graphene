import graphene
import json
from datetime import datetime
import uuid
import random


class Tweet(graphene.ObjectType):
    title = graphene.String()
    content = graphene.String()


class Player(graphene.ObjectType):
    id = graphene.ID(default_value=str(uuid.uuid4()))
    number = graphene.Int(default_value=str(random.randint(1, 99)))
    jerseyname = graphene.String()
    created_at = graphene.DateTime(default_value=datetime.now())


class RootQuery(graphene.ObjectType):
    players = graphene.List(Player, limit=graphene.Int())
    is_admin = graphene.Boolean()

    def resolve_is_admin(self, info):
        return True

    def resolve_players(self, info, limit=None):
        return [
            Player(number="99", jerseyname="Gretzky",
                   created_at=datetime.now()),
            Player(number="9", jerseyname="Kane", created_at=datetime.now()),
            Player(number="31", jerseyname="Niemi", created_at=datetime.now())
        ][:limit]


class CreatePlayer(graphene.Mutation):
    player = graphene.Field(Player)  # field in the class

    class Arguments:
        jerseyname = graphene.String()  # arguments the mutation allows

    def mutate(self, info, jerseyname):  # create the object and return a CreatePlayer object
        player = Player(jerseyname=jerseyname,
                        created_at=datetime.now())
        return CreatePlayer(player=player)


class CreateTweet(graphene.Mutation):
    tweet = graphene.Field(Tweet)

    class Arguments:
        title = graphene.String()
        content = graphene.String()

    def mutate(self, info, title, content):

        if info.context.get('is_anonymous'):
            raise Exception('Not Authenticated')

        tweet = Tweet(title=title,
                      content=content)
        return CreateTweet(tweet=tweet)


class RootMutation(graphene.ObjectType):
    create_player = CreatePlayer.Field()  # Class responsible for a mutation
    create_tweet = CreateTweet.Field()


mySchema = graphene.Schema(query=RootQuery, mutation=RootMutation)

if __name__ == '__main__':
    get = mySchema.execute(
        '''
        query ($limit: Int) {
             isAdmin
             players(limit: $limit) {
                 id
                 number
                 jerseyname
                 createdAt
             }
        }
        ''',
        variable_values={'limit': 2}
    )

    set = mySchema.execute(
        '''
        mutation ($jerseyname: String) {
            createPlayer(jerseyname: $jerseyname) {
                player {
                    id
                    number
                    jerseyname
                    createdAt
                }
            }
        }
        ''',
        variable_values={'jerseyname': 'Hunter'}
    )

    tweet = mySchema.execute(
        '''
    mutation {
        createTweet(title: "Hello", content: "World") {
            tweet {
                title
                content
            }
        }
    }
    ''',
        context={'is_anonymous': True}
    )

    getResult = dict(get.data.items())
    setResult = dict(set.data.items())
    tweetResult = dict(tweet.data.items())

    print(json.dumps(getResult, indent=2))
    print(json.dumps(setResult, indent=2))
    print(json.dumps(tweetResult, indent=2))
