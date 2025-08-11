## Run These 2 Files

- **`LoadFileOnDisk.java`** - Shows results for task 1 and task 2.
  _Run this only when there is no `disk_storage.dat` file._
  _This file takes in the data from 'games.txt', convert them into objects, and store it in 'disk_storage.dat' file._
  \_It also initializes a B+ tree with n = 7, bulk load the sorted keys into the B+ tree, and store the B+ tree in a database file.

- **`Task 3.java`** - Shows results for task 3.
  _Runs a brute force linear scan method and B+ Tree query method_
  \_

---

## How to Compile Classes

Inside the `project1` folder, run:

```sh
javac -d bin *.java
```

## How to run code:

Inside the `project1` folder, run this:

```sh
   java -cp bin LoadFileOnDisk
   java -cp bin Task3
```

### Note: The files below are not in use -

`PhysicalAddress.java`
`MappingTable.java`
