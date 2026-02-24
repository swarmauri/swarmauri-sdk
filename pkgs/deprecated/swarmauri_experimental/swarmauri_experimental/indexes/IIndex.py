from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

class IIndex(ABC):
    """
    An abstract interface class for generic indexing data structures.
    It defines a broad range of methods typically found in or needed by
    advanced index implementations, including:

    - Core Indexing: build, insert, delete, update, clear
    - Queries: nearest_neighbor, knn_search, range_search, range_count
    - Bulk/Batch operations: batch_insert, batch_delete
    - Persistence: save, load
    - Optimization/Maintenance: optimize, rebuild
    - Distance Function Management: set_distance_function, get_distance_function
    - Metadata: info, stats
    - Iteration over items: items
    - Concurrency (locks)
    - Sharding: split, merge
    - Advanced queries: knn_within_radius, mip_search (maximum inner product)
    - Advanced Persistence/Recovery & System Optimization:
          saveDatabase, loadDatabase, saveIndex, loadIndex, checkpoint, snapshot,
          write ahead logging, LSM Trees, atomic writes, buffer pools, caching
    """

    # --------------------- CORE INDEX BUILD & MODIFY ---------------------

    @abstractmethod
    def build_index(self, data: Iterable[Any]) -> None:
        """
        Build the index from an iterable of data items (documents, vectors, etc.).
        Some structures may do a batch build for efficiency.
        
        :param data: An iterable of items to index.
        """
        pass

    @abstractmethod
    def insert(self, item: Any) -> None:
        """
        Insert a single item into the index. This may cause re-balancing,
        splits, or expansions in the underlying data structure.

        :param item: The item (e.g., vector or document) to insert.
        """
        pass

    @abstractmethod
    def delete(self, item: Any) -> None:
        """
        Remove an existing item from the index. May require merging nodes
        or reducing coverage in hierarchical structures.

        :param item: The item to be removed. Matching criteria (reference vs. content)
                     depends on the implementation.
        """
        pass

    @abstractmethod
    def update(self, old_item: Any, new_item: Any) -> None:
        """
        Update the index by replacing one item with another. Often implemented
        internally as delete(old_item) + insert(new_item).

        :param old_item: Existing item in the index.
        :param new_item: New item to replace the old_item.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Remove all items and reset the index to an empty state.
        May re-initialize or discard internal data structures.
        """
        pass

    # --------------------- BULK / BATCH OPERATIONS ---------------------

    @abstractmethod
    def batch_insert(self, items: Iterable[Any]) -> None:
        """
        Insert multiple items in a single operation. Can be more efficient
        than repeated single-item inserts if the implementation supports
        batch optimizations.

        :param items: An iterable of items to insert.
        """
        pass

    @abstractmethod
    def batch_delete(self, items: Iterable[Any]) -> None:
        """
        Remove multiple items in a single operation.

        :param items: An iterable of items to remove.
        """
        pass

    # --------------------- QUERY / SEARCH OPERATIONS ---------------------

    @abstractmethod
    def nearest_neighbor(self, query: Any) -> Tuple[Any, float]:
        """
        Find the single closest item to the query in the metric or vector space.

        :param query: Query item (e.g., vector, document).
        :return: (closest_item, distance)
        """
        pass

    @abstractmethod
    def knn_search(self, query: Any, k: int) -> List[Tuple[Any, float]]:
        """
        Find the k-nearest neighbors for the query.

        :param query: Query item.
        :param k: Number of neighbors to retrieve.
        :return: A list of (item, distance), sorted by increasing distance.
        """
        pass

    @abstractmethod
    def range_search(self, query: Any, radius: float) -> List[Any]:
        """
        Return all items within 'radius' of the query.

        :param query: Query item.
        :param radius: Distance threshold.
        :return: A list of items.
        """
        pass

    # --------------------- ADVANCED / EXTENDED QUERIES ---------------------

    @abstractmethod
    def range_count(self, query: Any, radius: float) -> int:
        """
        Return the number of items within 'radius' of the query,
        without necessarily listing them.

        :param query: Query item.
        :param radius: Distance threshold.
        :return: Integer count of items within the radius.
        """
        pass

    @abstractmethod
    def knn_within_radius(self, query: Any, k: int, radius: float) -> List[Tuple[Any, float]]:
        """
        A combined approach: retrieve up to k nearest neighbors,
        but only if they fall within 'radius'. If fewer than k
        items are within the radius, return fewer.

        :param query: The query item.
        :param k: Max number of neighbors to return.
        :param radius: Distance threshold.
        :return: A list of (item, distance) satisfying distance <= radius.
        """
        pass

    # --------------------- DISTANCE FUNCTION MANAGEMENT ---------------------

    @abstractmethod
    def set_distance_function(self, distance_fn: Callable[[Any, Any], float]) -> None:
        """
        Update the distance/similarity metric used by the index.
        Not all index structures can adapt to a new distance function
        without a full rebuild, so the implementation may vary.

        :param distance_fn: A callable accepting (item1, item2) -> distance float.
        """
        pass

    @abstractmethod
    def get_distance_function(self) -> Callable[[Any, Any], float]:
        """
        Return the current distance function used by the index.
        """
        pass

    # --------------------- OPTIMIZATION / MAINTENANCE ---------------------

    @abstractmethod
    def rebuild(self) -> None:
        """
        Completely rebuild the index from its current items,
        potentially achieving better structure than incremental changes.
        This may be a no-op if the data structure doesn't require it.
        """
        pass

    # --------------------- PERSISTENCE ---------------------

    @abstractmethod
    def save(self, filepath: str) -> None:
        """
        Persist the index and its data structures to disk at the specified path.
        For large indexes, this may involve writing multiple files or a specialized format.

        :param filepath: Where to save the index (e.g., local file path).
        """
        pass

    @abstractmethod
    def load(self, filepath: str) -> None:
        """
        Load a previously saved index from disk, restoring internal structures
        so that queries can be executed as if it was never unloaded.

        :param filepath: Filepath or directory containing the saved index data.
        """
        pass

    # --------------------- METADATA / DIAGNOSTICS ---------------------

    @abstractmethod
    def size(self) -> int:
        """
        Return the current number of items stored in the index.
        """
        pass

    @abstractmethod
    def info(self) -> Dict[str, Any]:
        """
        Return a dictionary of metadata or structural info about the index.
        Could include:
          - index type
          - number of nodes
          - tree height
          - memory usage
          - disk usage
          - dimension (if applicable)
        """
        pass

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """
        Return a dictionary of runtime statistics or performance counters,
        like average query time, number of expansions, concurrency metrics, etc.
        """
        pass

    # --------------------- ITERATION / FULL SCAN ---------------------

    @abstractmethod
    def items(self) -> Iterable[Any]:
        """
        Provide an iterator or list of all items in the index.
        This allows for a full scan if needed.

        :return: An iterable of items.
        """
        pass

    # --------------------- CONCURRENCY / LOCKS ---------------------

    @abstractmethod
    def acquire_read_lock(self) -> None:
        """
        Acquire a read lock for concurrent scenarios. If the index supports
        multiple readers and single writer, this can ensure consistency.
        """
        pass

    @abstractmethod
    def acquire_write_lock(self) -> None:
        """
        Acquire a write lock before mutating the index (insert, delete, etc.).
        """
        pass

    @abstractmethod
    def release_lock(self) -> None:
        """
        Release a previously acquired lock (either read or write),
        concluding the locked section of code.
        """
        pass

    # --------------------- SHARDING / PARTITIONING ---------------------

    @abstractmethod
    def split(self, shard_key: Callable[[Any], int]) -> List['IIndex']:
        """
        Partition the index into multiple shards based on 'shard_key'.
        Each shard is returned as a separate index instance containing
        a subset of items.

        :param shard_key: A function mapping an item to a shard ID (e.g. hash-based).
        :return: A list of new index instances, each containing a partition of the data.
        """
        pass

    @abstractmethod
    def merge(self, other: 'IIndex') -> None:
        """
        Merge another index (of the same type) into the current one, combining
        all items. This might be used after parallel indexing or in distributed
        settings. The merging logic can vary widely by index structure.

        :param other: Another index instance containing items to be merged.
        """
        pass

    # --------------------- ADVANCED PERSISTENCE & SYSTEM OPTIMIZATION ---------------------

    @abstractmethod
    def save_database(self, filepath: str) -> None:
        """
        Persist the entire database—including all indexes and configurations—to disk.

        :param filepath: Destination path for the database snapshot.
        """
        pass

    @abstractmethod
    def load_database(self, filepath: str) -> None:
        """
        Load an entire database from disk, restoring all indexes and configurations.

        :param filepath: Source path of the database snapshot.
        """
        pass

    @abstractmethod
    def save_index(self, index_id: str, filepath: str) -> None:
        """
        Save a specific index (identified by index_id) to disk.

        :param index_id: Identifier for the index.
        :param filepath: Destination path for saving the index.
        """
        pass

    @abstractmethod
    def load_index(self, index_id: str, filepath: str) -> None:
        """
        Load a specific index from disk, identified by index_id.

        :param index_id: Identifier for the index.
        :param filepath: Source path containing the saved index.
        """
        pass

    @abstractmethod
    def checkpoint(self) -> None:
        """
        Create a checkpoint of the current state of the index or database.
        This checkpoint can be used for recovery to a known good state.
        """
        pass

    @abstractmethod
    def snapshot(self) -> Any:
        """
        Create a snapshot of the current state of the index or database.
        The returned snapshot can be used for backup or recovery purposes.

        :return: An object representing the snapshot state.
        """
        pass

    @abstractmethod
    def write_ahead_log(self, record: Any) -> None:
        """
        Write a record to the write-ahead log (WAL) for durability.
        This ensures that operations can be recovered in the event of a crash.

        :param record: The log record to persist.
        """
        pass

    @abstractmethod
    def flush_write_ahead_log(self) -> None:
        """
        Flush the write-ahead log, ensuring that all pending log records are
        written to durable storage.
        """
        pass

    @abstractmethod
    def enable_lsm_tree(self) -> None:
        """
        Enable Log-Structured Merge Tree (LSM Tree) support to optimize write-intensive workloads.
        """
        pass

    @abstractmethod
    def disable_lsm_tree(self) -> None:
        """
        Disable Log-Structured Merge Tree (LSM Tree) support if it is currently enabled.
        """
        pass

    @abstractmethod
    def is_lsm_enabled(self) -> bool:
        """
        Check whether LSM Tree support is currently enabled.

        :return: True if LSM Trees are enabled, otherwise False.
        """
        pass

    @abstractmethod
    def atomic_write(self, write_operation: Callable[[], None]) -> None:
        """
        Execute the provided write operation atomically. This ensures that the operation either
        completes fully or has no effect, even in the presence of failures.

        :param write_operation: A callable that encapsulates the write operations.
        """
        pass

    @abstractmethod
    def get_buffer_pool(self) -> Any:
        """
        Retrieve the current buffer pool used by the index for caching and I/O operations.

        :return: The buffer pool object.
        """
        pass

    @abstractmethod
    def set_buffer_pool(self, pool: Any) -> None:
        """
        Set or update the buffer pool used by the index.

        :param pool: The new buffer pool to be used.
        """
        pass

    @abstractmethod
    def cache_item(self, key: Any, value: Any) -> None:
        """
        Cache an item in the index's caching system to improve read performance.

        :param key: Identifier for the cached item.
        :param value: The item to be cached.
        """
        pass

    @abstractmethod
    def get_cached_item(self, key: Any) -> Optional[Any]:
        """
        Retrieve an item from the cache.

        :param key: Identifier for the cached item.
        :return: The cached item if available, otherwise None.
        """
        pass

    @abstractmethod
    def clear_cache(self) -> None:
        """
        Clear all cached items from the index's cache.
        """
        pass
