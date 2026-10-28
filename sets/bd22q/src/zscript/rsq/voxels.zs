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

	// 2.0: spent casings follow the Spent casings option from the moment they are thrown and are
	// left alone when it changes. Each was sized for what it got at spawn (a real-size mesh at
	// 1.0, or BD22's sprite / voxel at BD22's scale), so swapping its model afterwards would draw
	// one at the other's scale.
	bool IsCasing(Actor a)
	{
		int c = CatOf(a);
		return c >= 0 && RSQ_VoxTable.Holder(c) == 'RSV_Casings';
	}

	int CatOf(Actor a)
	{
		int s = a.sprite;
		return s >= 0 && s < sprCat.Size() ? sprCat[s] - 1 : -1;
	}

	// lend (or take back) the category's voxel; true once the actor's sprite has a category
	//
	// 2.0 (owner: "a GIGANTIC shell casing when the AssaultShotgun fires"): only an option CHANGE
	// (retro) takes a model back. On a fresh actor (spawn, pending) A_ChangeModel('None') was never
	// a no-op: RSA_Casings runs first and has already lent the real 12 ga hull / rifle case
	// (casemodels.zs) and set the actor's scale to 1.0, because the mesh is real-size. Taking that
	// back left BD22's own C4S2 / C4S3 casing sprite drawn at scale 1.0: 4x (hull, BD 0.25) to 6.7x
	// (rifle brass, BD 0.15) its size, right at the port. Rig 2.0-int: ShotgunCasing scale 1.000
	// with the hull stripped, a 21 x 10 unit red hull filling the eye and side frames.
	bool Apply(Actor a, int mask, bool retro = false)
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
		else if (retro)
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
			if (!a.player && !a.bIsMonster && !IsCasing(a))
				Apply(a, m, true);
	}
}

// The BD voxel pack (made for an older Brutal Doom) replaces "DeathSphere", which BD22 no longer
// has; DECORATE stops the whole game on a missing replaced type. ZScript is compiled first, so
// this empty stand-in lets the voxel pack load. It is never spawned.
class DeathSphere : Inventory {}
