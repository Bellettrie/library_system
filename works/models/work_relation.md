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
    Series: BookCode
    Work : Title
    Work : SubTitle
    Work <-- CreatorToWork
    CreatorToWork --> Creator
    Creator: FirstName
    Creator: LastName
    Work <-- WorkRelation:source_work
    Work <-- WorkRelation:target_work
    WorkRelation: Type
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
    
    Hitchhikers_Guide_Series --> Hitchhikers_Guide:part_of_series
    Hitchhikers_Guide_Series --> Restaurant_end_Universe:part_of_series
    Hitchhikers_Guide_Series --> Life_Universe_Everything:part_of_series
    Hitchhikers_Guide_Series --> So_Long_Thanks_Fish:part_of_series
    Hitchhikers_Guide_Series --> Young_Zaphod_Plays_Safe:part_of_series
    Hitchhikers_Guide_Series --> Mostly_Harmless:part_of_series
```

We have multiple use-cases that require recursively traversing this graph. To facilitate this, the WorkRelation class has a method called `traverse_relations`.

Here's some examples of how it works.
