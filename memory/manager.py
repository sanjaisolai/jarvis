from langmem import create_memory_manager

from llm.jarvis import memory_llm
from memory.schemas import UserMemory
from memory.pinecone_service import search_memories, update_memory
from langmem.knowledge.extraction import ExtractedMemory
MEMORY_INSTRUCTIONS = """
You are the long-term memory manager for Jarvis.

Your job is to identify durable information about the USER.

Remember things such as:

- User's personal details like name, age, location, etc.
- User preferences  
- User's technical skills
- User's projects
- User's goals
- User's recurring working patterns
- Important user-specific context
- Explicit requests to remember something

DO NOT remember:

- Temporary questions
- Weather
- News results
- Tool results
- General knowledge
- Casual conversation
- Information unrelated to the user

Every memory must be self-contained.

Example 1:

User:
"I prefer Python over Java."

Memory:
"User prefers Python over Java as his programming language."

Example 2:

User:
"Give me the code in java as i am working in it in AA"

Memory:
"User prefers java in project AA"

If new information changes an existing memory,
update the existing memory instead of creating a duplicate.

If the user explicitly asks Jarvis to forget something,
delete the corresponding memory.

important storing rules:
Always give the context in the content too.
eg 1: User prefers Python - BAD, User prefers python as his programming language - GOOD
eg 2: User prefers US, Spain - BAD, User prefers US, Spain as his vacation destination - GOOD
"""


memory_manager = create_memory_manager(
    memory_llm,
    schemas=[UserMemory],
    instructions=MEMORY_INSTRUCTIONS,
    enable_inserts=True,
    enable_updates=True,
    enable_deletes=True,
)

async def process_memory(
    user_id: str,
    conversation: list
):


    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation
    )

    existing_memories = search_memories(
        user_id=user_id,
        query=conversation_text,
        top_k=10
    )
#[ExtractedMemory(id='974980e7-0f12-461a-a774-79ff396772a4', content=UserMemory(category='preference', content='User prefers Java', importance=8))]
    # print("\nExisting memories:")
    # print(existing_memories)
    langmem_existing_memory = []
    existing_id_dict = {}
    if existing_memories:
        for mem in existing_memories:
            obj = ExtractedMemory(id=mem['id'], content=UserMemory(category=mem['category'],content=mem['content'],importance=mem['importance']))
            langmem_existing_memory.append(obj)
            existing_id_dict[mem['id']]={'category':mem['category'],'content':mem['content'],'importance':mem['importance']}

        
    result = await memory_manager.ainvoke({
        "messages": conversation,
        "existing": langmem_existing_memory
    })
    # insert into pinecone of result exists
    if len(result)>0:
        for i in range(len(result)):
            id = result[i].id
            if id in existing_id_dict:

                if ( result[i].content.content != existing_id_dict[id]['content']
                    or result[i].content.importance != existing_id_dict[id]['importance']
                    or result[i].content.category != existing_id_dict[id]['category'] ):
                    
                    update_memory(user_id=user_id, 
                                  memory_id=result[i].id, content=result[i].content.content, 
                                  importance=result[i].content.importance, 
                                  category=result[i].content.category
                    )


            else:
                update_memory(user_id=user_id, 
                            memory_id=result[i].id, content=result[i].content.content, 
                            importance=result[i].content.importance, 
                            category=result[i].content.category
                )

    return result


