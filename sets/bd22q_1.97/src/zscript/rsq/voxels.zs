// RS voxel pickups (1.24, owner). The BD voxel pack's voxels, shown per category: Voxel Options
// has Weapons, Ammo, Health, Armor, Keys, Powerups, Decorations and Spent casings.
//
// How: the voxel pack's own VOXELDEF swaps a sprite for its voxel everywhere, always. Ours
// replaces it with an empty one (load the voxel pack BEFORE this pack) and keeps the voxels as
// models on one holder class per category (MODELDEF.rsqvox, generated). An actor whose sprite is
// one of a category's is lent that holder's models (A_ChangeModel's modeldef) while the
// category is on; frames the holder has no voxel for stay sprites.
//
// Without the voxel pack loaded the holders have no models and everything stays a sprite.
// The options are what YOU see: they are read for the local player only and change nothing
// the game simulates, so they are safe in netplay.
class RSQ_Voxels : EventHandler
{
	Array<int> sprCat;		// sprite index -> category + 1 (0: none)
	Array<Actor> pending;	// spawned this tic or last: their first frames may not be their own yet
	Array<int> pendingAge;
	int lastMask;
	int blank;				// TNT1: the blank frame many pickups open on
	// 1.28 (owner: "I pick them up and get sprites"): a pickup that is picked up BECOMES the item
	// in your inventory, and a weapon's held (HUD) model is looked up through the same model
	// override. A voxel lent to a pickup must be taken back the moment it has an owner, or the
	// held weapon finds no model and is drawn as a sprite.
	Array<Inventory> lent;

	override void WorldLoaded(WorldEvent e)
	{
		Array<Name> names;
		Array<int> cats;
		RSQ_VoxTable.Sprites(names, cats);
		for (int i = 0; i < names.Size(); i++)
		{
			int s = Actor.GetSpriteIndex(names[i]);
			if (s < 0)
				continue;
			while (sprCat.Size() <= s)
				sprCat.Push(0);
			sprCat[s] = cats[i] + 1;
		}
		lastMask = Mask();
		blank = Actor.GetSpriteIndex('TNT1');
	}

	static int Mask()
	{
		int m = 0;
		if (consoleplayer < 0 || consoleplayer >= MAXPLAYERS)
			return m;
		for (int i = 0; i < RSQ_VoxTable.COUNT; i++)
		{
			let cv = CVar.GetCVar(RSQ_VoxTable.CVarName(i), players[consoleplayer]);
			if (cv ? cv.GetBool() : RSQ_VoxTable.Defaults(i) != 0)
				m |= 1 << i;
		}
		return m;
	}

	int CatOf(Actor a)
	{
		int s = a.sprite;
		return s >= 0 && s < sprCat.Size() ? sprCat[s] - 1 : -1;
	}

	// lend (or take back) the category's voxel; true once the actor's sprite has a category
	bool Apply(Actor a, int mask)
	{
		int c = CatOf(a);
		if (c < 0)
			return false;
		let inv = Inventory(a);
		if (inv && inv.Owner)
			return true;		// owned: never lend (and see TakeBack)
		if (mask & (1 << c))
		{
			a.A_ChangeModel(RSQ_VoxTable.Holder(c));
			if (inv && lent.Find(inv) == lent.Size())
				lent.Push(inv);
		}
		else
			a.A_ChangeModel('None');
		return true;
	}

	override void WorldThingSpawned(WorldEvent e)
	{
		let a = e.Thing;
		if (!a || a.player || a.bIsMonster || sprCat.Size() == 0)
			return;
		if (!Apply(a, lastMask) && a.sprite == blank)
		{
			// many pickups open on a blank frame and show their own sprite a tic later
			pending.Push(a);
			pendingAge.Push(0);
		}
	}

	override void WorldTick()
	{
		if (sprCat.Size() == 0)
			return;
		// picked up since last tic: give it back its own models
		for (int i = lent.Size() - 1; i >= 0; i--)
		{
			let inv = lent[i];
			if (!inv)
			{
				lent.Delete(i);
				continue;
			}
			if (inv.Owner)
			{
				inv.A_ChangeModel('None');
				lent.Delete(i);
			}
		}
		for (int i = pending.Size() - 1; i >= 0; i--)
		{
			let a = pending[i];
			if (!a || Apply(a, lastMask) || ++pendingAge[i] > 2)
			{
				pending.Delete(i);
				pendingAge.Delete(i);
			}
		}
		// an option changed: everything already in the level follows it
		int m = Mask();
		if (m == lastMask)
			return;
		lastMask = m;
		let it = ThinkerIterator.Create('Actor');
		Actor a;
		while (a = Actor(it.Next()))
			if (!a.player && !a.bIsMonster)
				Apply(a, m);
	}
}

// The BD voxel pack (made for an older Brutal Doom) replaces "DeathSphere", which BD22 no longer
// has; DECORATE stops the whole game on a missing replaced type. ZScript is compiled first, so
// this empty stand-in lets the voxel pack load. It is never spawned.
class DeathSphere : Inventory {}
