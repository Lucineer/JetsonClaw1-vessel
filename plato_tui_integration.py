
"""
Plato-TUI Integration Bridge
Connects our tiling substrate to plato-tui's I2IClient.
"""

from plato_notebook_v2 import PlatoNotebook

class PlatoTUIIntegration:
    """Bridge between plato-tui and our tile network."""
    
    def __init__(self):
        self.plato = PlatoNotebook()
        print(f"Integration bridge ready with {len(self.plato.substrate.tiles)} tiles")
    
    def handle_user_input(self, user_input: str) -> dict:
        """Process user input from TUI, return response for rendering."""
        # Check constraints first
        constraint_result = self.plato.constraint_check(user_input)
        
        response = {
            "input": user_input,
            "constraint_result": constraint_result['result'],
            "violations": constraint_result['violations'],
            "unresolved_anchors": constraint_result['unresolved_anchors']
        }
        
        # If allowed, process TUTOR_JUMP anchors
        if constraint_result['result'] == "Allow":
            import re
            anchors = re.findall(r'\[([^\]]+)\]', user_input)
            tutor_jumps = []
            
            for anchor in anchors:
                content = self.plato.substrate.tutor_jump(anchor)
                tutor_jumps.append({
                    "anchor": anchor,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content,
                    "tile_found": not content.startswith("No tiles found")
                })
            
            response["tutor_jumps"] = tutor_jumps
            
            # Build context for rendering
            relevant_tiles = self.plato.substrate.retrieve_relevant_tiles(user_input, max_tiles=3)
            context_tiles = []
            for tile in relevant_tiles:
                context_tiles.append({
                    "id": tile.tile_id,
                    "question": tile.question,
                    "answer_preview": tile.answer[:150] + "..." if len(tile.answer) > 150 else tile.answer,
                    "tags": tile.tags
                })
            
            response["context_tiles"] = context_tiles
            
            # Calculate token reduction
            full_context = "".join(tile.answer for tile in self.plato.substrate.tiles.values())
            full_tokens = len(full_context.split())
            
            tiled_context = "".join(tile.answer[:200] for tile in relevant_tiles)
            tiled_tokens = len(tiled_context.split())
            
            if full_tokens > 0:
                reduction = (1 - tiled_tokens / full_tokens) * 100
                response["token_reduction"] = f"{reduction:.1f}%"
                response["tokens_saved"] = full_tokens - tiled_tokens
        
        return response
    
    def get_available_anchors(self) -> list:
        """Get all available word anchors for TUTOR_JUMP."""
        anchors = []
        for tile in self.plato.substrate.tiles.values():
            anchors.extend(tile.tags)
        return sorted(set(anchors))
    
    def get_tile_stats(self) -> dict:
        """Get tile network statistics."""
        total_tiles = len(self.plato.substrate.tiles)
        total_tags = sum(len(tile.tags) for tile in self.plato.substrate.tiles.values())
        unique_tags = len(self.get_available_anchors())
        
        # Usage statistics
        usage_counts = [tile.usage_count for tile in self.plato.substrate.tiles.values()]
        
        return {
            "total_tiles": total_tiles,
            "total_tags": total_tags,
            "unique_anchors": unique_tags,
            "avg_usage": sum(usage_counts) / max(1, total_tiles),
            "most_used_tile": max(self.plato.substrate.tiles.values(), key=lambda t: t.usage_count).tile_id if usage_counts else None
        }
