import 'pinia'
import type { StateTree } from 'pinia'

declare module 'pinia' {
  interface DefineStoreOptionsBase<S extends StateTree, Store> {
    persist?:
      | boolean
      | {
          key?: string
          pick?: string[]
          paths?: string[]
          storage?: Storage
          serializer?: {
            serialize: (value: unknown) => string
            deserialize: (value: string) => unknown
          }
        }
  }
}

export {}
