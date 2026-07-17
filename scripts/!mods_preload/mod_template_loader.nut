::ModTemplate <- {
	ID = "mod_template",
	Name = "Battle Brothers Mod Template",
	Version = "0.1.0"
};

::ModTemplate.HookMod <- ::Hooks.register(::ModTemplate.ID, ::ModTemplate.Version, ::ModTemplate.Name);
::ModTemplate.HookMod.require("mod_msu >= 1.9.0");
