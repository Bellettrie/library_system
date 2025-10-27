# WorkRelation
The WorkRelation model is used to store all relations between works. Some definitions of the classes:

- Work: The concept of some creative effort (series, publication, sub_work, etc)
- WorkRelation: describes the relation between two works
- CreatorToWork: describes the relation between a creator and a Work
- Creator: A person with a creative role in the production of works.
- Item: tracks a physical object that is a copy of a specific work.
- Series: A work with some extra info on where it should be located in the library.
  - Conceptually a series is a set of works that belong together. For instance, dune, lord of the rings, etc.

## Full Data Model
For context on how to reason about the WorkRelation, here's the data model that describes the information about works.
```mermaid
classDiagram
    Work <|-- Series
    Work <-- Item:copy_of
    Item: BookCode
    Item: moreData
    Series: BookCode
    Work : Title
    Work : SubTitle
    Work:  MoreData
    Work <-- CreatorToWork
    CreatorToWork: numberInfo
    CreatorToWork: role
    CreatorToWork --> Creator
    Creator: FirstName
    Creator: LastName
    Work <-- WorkRelation:from_work
    Work <-- WorkRelation:to_work
    WorkRelation: relationKind
    WorkRelation: positionNumeric
    WorkRelation: positionText
```


## Traversing the WorkRelations
Since the WorkRelation class has a source and a target, we can "walk" from work to work by following WorkRelation arrows. These "walking" options can be interpreted as a graph, where a node describes a specific work, every arrow a relationship between them.
Lets consider this example graph.  

```mermaid
classDiagram
    Ultimate_Hitchhikers_Guide <-- Hitchhikers_Guide:subwork_of
    Ultimate_Hitchhikers_Guide <-- Restaurant_end_Universe:subwork_of
    Ultimate_Hitchhikers_Guide <-- Life_Universe_Everything:subwork_of
    Ultimate_Hitchhikers_Guide <-- So_Long_Thanks_Fish:subwork_of
    Ultimate_Hitchhikers_Guide <-- Young_Zaphod_Plays_Safe:subwork_of
    Ultimate_Hitchhikers_Guide <-- Mostly_Harmless:subwork_of
    
    Hitchhikers_Guide --> Hitchhikers_Guide_Series:part_of_series
    Restaurant_end_Universe --> Hitchhikers_Guide_Series:part_of_series
    Life_Universe_Everything --> Hitchhikers_Guide_Series:part_of_series
    So_Long_Thanks_Fish --> Hitchhikers_Guide_Series:part_of_series
    Young_Zaphod_Plays_Safe --> Hitchhikers_Guide_Series:part_of_series
    Mostly_Harmless --> Hitchhikers_Guide_Series:part_of_series
```

We have multiple use-cases that require recursively traversing this graph. To facilitate this, the WorkRelation class has a method called `traverse_relations`.

Here's some examples of how it works.
### Example 1: Finding search terms for the Ultimate Hitchhikers Guide
When finding search terms for a book, we want to traverse both the subwork-relation, as well as the part_of_series relation.
We need to traverse the part_of_series relation in forwards direction, but the subwork_of relation in reverse.

### Example 2: All works authored by Douglas Adams
This query starts from all works directly linked to douglas adams, and follows the part_of_series relationship in reverse. 
Hence, in this example it would start from Hitchhikers Guide Series to the middle row of works.