#include "buildingLoads.h"

#include "addToRunTimeSelectionTable.H"
#include "OFstream.H"
#include "OSspecific.H"
#include "volFields.H"

namespace Foam
{

defineTypeNameAndDebug(buildingLoads, 0);

addToRunTimeSelectionTable(functionObject, buildingLoads, dictionary);


buildingLoads::buildingLoads(const word& name, const Time& runTime, const dictionary& dict)
    : fvMeshFunctionObject(name, runTime, dict), patchName_(""), pressureFieldName_(""), patchID_(-1)
{
    read(dict);
}


// Read configuration

bool buildingLoads::read(const dictionary& dict)
{
    fvMeshFunctionObject::read(dict);

    dict.readIfPresent("patch", patchName_);
    dict.readIfPresent("pressureField", pressureFieldName_);

    patchID_ = mesh_.boundaryMesh().findPatchID(patchName_);

    if (patchID_ < 0)
        FatalErrorInFunction << "Cannot find patch " << patchName_ << exit(FatalError);

    return true;
}


// Execute

bool buildingLoads::execute()
{
    return true;
}


// Write results

bool buildingLoads::write()
{
    // Retrieve the pressure field
    const volScalarField& p = mesh_.lookupObject<volScalarField>(pressureFieldName_);

    // Retrieve the building patch
    const fvPatch& patch = mesh_.boundary()[patchID_];

    const vectorField& Sf = patch.Sf();
    const vectorField& Cf = patch.Cf();

    const scalarField& pPatch = p.boundaryField()[patchID_];

    // Create output directory
    const fileName outputDir = mesh_.time().globalPath() / "postProcessing" / "buildingLoads";

    mkDir(outputDir);

    // One CSV file per timestep
    const fileName outputFile = outputDir / (mesh_.time().timeName() + ".csv");

    OFstream file(outputFile);

    // CSV header

    file
        << "faceID,"
        << "x,y,z,"
        << "area,"
        << "pressure,"
        << "Fx,Fy,Fz,"
        << "forceMagnitude"
        << nl;

    // Loop over faces

    forAll(Sf, faceI)
    {
        const scalar area = mag(Sf[faceI]);

        const vector centre = Cf[faceI];

        const scalar pressure = pPatch[faceI];

        // Pressure force on the solid.
        // Sf is oriented outward from the fluid cell.

        const vector force = -pressure * Sf[faceI];

        const scalar forceMagnitude = mag(force);

        file
            << faceI << ","
            << centre.x() << ","
            << centre.y() << ","
            << centre.z() << ","
            << area << ","
            << pressure << ","
            << force.x() << ","
            << force.y() << ","
            << force.z() << ","
            << forceMagnitude
            << nl;
    }

    Info << "buildingLoads: wrote " << outputFile << endl;

    return true;
}

}
