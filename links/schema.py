import graphene
from graphene_django import DjangoObjectType

from .models import Link
from users.schema import UserType
from links.models import Link, Vote
from graphql import GraphQLError
from django.db.models import Q


class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


class Query(graphene.ObjectType):
    links = graphene.List(LinkType, search=graphene.String())
    votes = graphene.List(VoteType)

    def resolve_links(self, info, search=None, **kwargs):
        if search:
            filter = (
                Q(title__icontains=search) |
                Q(director__icontains=search)
            )
            return Link.objects.filter(filter)

        return Link.objects.all()

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()


class CreateLink(graphene.Mutation):
    id = graphene.Int()
    title = graphene.String()
    director = graphene.String()
    genre = graphene.String()
    releaseYear = graphene.Int()
    duration = graphene.Int()
    imageUrl = graphene.String()
    posted_by = graphene.Field(UserType)

    class Arguments:
        title = graphene.String()
        director = graphene.String()
        genre = graphene.String()
        releaseYear = graphene.Int()
        duration = graphene.Int()
        imageUrl = graphene.String()

    def mutate(self, info, title, director, genre, releaseYear, duration, imageUrl):
        user = info.context.user or None

        link = Link(title=title, director=director, genre=genre, releaseYear=releaseYear, duration=duration, imageUrl=imageUrl)
        link.save()

        return CreateLink(
            id=link.id,
            title=link.title,
            director=link.director,
            genre=link.genre,
            releaseYear=link.releaseYear,
            duration=link.duration,
            imageUrl=link.imageUrl,
            posted_by=link.posted_by,
        )

class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link,
        )

        return CreateVote(user=user, link=link)


class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()
